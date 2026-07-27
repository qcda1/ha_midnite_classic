#!/usr/bin/env python

# --------------------------------------------------------------------------- #
# Handle the modbus data from the Classic.
# The only method called out of this is getModbusData
# This opens the client to the Classic, gets the data and closes it. It does not
# keep the link open to the Classic.
#
# Based on https://github.com/ClassicDIY/ClassicMQTT
#
# 
# # --------------------------------------------------------------------------- #


from pymodbus.client import ModbusTcpClient as ModbusClient
from .Payload import BinaryPayloadDecoder, Endian
from collections import OrderedDict
import logging
import sys

log = logging.getLogger("classic_modbusdecoder")


# --------------------------------------------------------------------------- #
# Read holding registers from an already-connected client
# --------------------------------------------------------------------------- #
def _readRegisters(theClient, addr, cnt):
    try:
        result = theClient.read_holding_registers(addr, count=cnt)
        if result.function_code >= 0x80:
            log.error(
                f"error getting addr={addr} cnt={cnt}, function_code={result.function_code}"
            )
            return {}
    except Exception as ex:
        log.error(f"Error getting addr={addr} cnt={cnt}, exception: {ex}")
        return {}
    return result.registers


# --------------------------------------------------------------------------- #
# Return a decoder for the passed in registers
# --------------------------------------------------------------------------- #
def getDataDecoder(registers):
    return BinaryPayloadDecoder.fromRegisters(
        registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE
    )


# --------------------------------------------------------------------------- #
# Lookup tables — texts taken verbatim from the manufacturer documentation:
# "MidNite Solar MODBUS Network Spec. Rev C.5 — December 8, 2013"
# (docs/classic_register_map_Rev-C5-December-8-2013.pdf)
# --------------------------------------------------------------------------- #

# Table 4120-1 — Charge Stage (register 4120 MSB)
CHARGE_STAGE_TEXT = {
    0: "Resting",
    3: "Absorb",
    4: "Bulk MPPT",
    5: "Float",
    6: "Float MPPT",
    7: "Equalize",
    10: "HyperVOC",
    18: "Equalize MPPT",
}

# Tables 4165-1 / 4165-2 — AUX 1 & AUX 2 Off – Auto – On
#   0 = output forced OFF (0 V)
#   1 = output operates automatically as defined in AuxNFunction
#   2 = output forced ON (~14 V)
#   3 = unassigned at present
AUX_OFF_AUTO_ON = {
    0: "AUX Off",
    1: "AUX Auto",
    2: "AUX On",
    3: "Unimplemented",
}

# Table 4165-3 — AUX 1 Function (Aux12Function bits 0-5)
# NOTE: values 22 and 23 (SOC%) are not in Rev C.5 of the spec; they were added
# in later Classic firmware and are kept here because they are what drives
# generator start/stop on SOC.
AUX1_FUNCTION_TEXT = {
    1:  "DIVERSION SLOW HIGH",      # Non-PWM On at Vbatt > Aux1VoltsHiAbs (after Delay time), Off at Vbatt < Aux1VoltsLoAbs (after Hold time)
    2:  "Low Battery Disconnect High",  # Same as DIVERSION SLOW HIGH but Active Low
    3:  "WASTE NOT HIGH",           # Non-PWM On at Vbatt > Aux1VoltsHiAbs, Off at Vbatt < Aux1VoltsLoAbs (Active High)
    4:  "WASTE NOT LOW",            # Non-PWM On at Vbatt > Aux1VoltsHiAbs, Off at Vbatt < Aux1VoltsLoAbs (Active Low)
    5:  "RESERVED",                 # Unimplemented
    6:  "RESERVED",                 # Unimplemented
    7:  "PV V ON HIGH",             # Active High if Vin > Aux1VoltsHiPv (after Delay time); off if Vin < Aux1VoltsLoPv after Hold time
    8:  "PV V ON LOW",              # Active Low if Vin > Aux1VoltsHiPv (after Delay time); on if Vin < Aux1VoltsLoPv after Hold time
    9:  "RESERVED",                 # Unimplemented
    10: "RESERVED",                 # Unimplemented
    11: "RESERVED",                 # Unimplemented
    12: "RESERVED",                 # Unimplemented
    13: "TOGGLE TEST",              # Output toggles once per second On-Off-On-Off automatically
    14: "NIGHT LIGHT HIGH",         # Active High On at Dawn, Off at Dusk
    15: "DAY LIGHT HIGH",           # Active High Off at Dawn, On at Dusk
    16: "WIND CLIPPER CONTROL",     # High when Vin > last Vin that yielded Absorb/Float/EQ, plus 5.0 V of headroom
    17: "FLOAT HIGH",               # Output On when Floating, Off when not Float, after 2 seconds
    18: "FLOAT LOW",                # Output Off when Floating, On when not Float, after 2 seconds
    19: "VENT FAN HIGH",            # On when Vbatt > Aux1VoltsHiAbs after 1 s; Off when Vbatt < Aux1VoltsHiAbs after 30 s
    20: "VENT FAN LOW",             # Off when Vbatt > Aux1VoltsHiAbs after 1 s; On when Vbatt < Aux1VoltsHiAbs after 30 s
    21: "GFP TRIP HIGH",            # Output On for ~0.150 seconds when a Ground Fault occurs
    22: "SOC% HIGH",                # Later firmware — Active High on State Of Charge threshold
    23: "SOC% LOW",                 # Later firmware — Active Low on State Of Charge threshold
}

# Table 4165-4 — AUX 2 Function (Aux12Function bits 8-13)
AUX2_FUNCTION_TEXT = {
    0:  "DIVERSION HIGH PWM",       # Digital Out PWM Battery Diversion (Active High)
    1:  "DIVERSION LOW PWM",        # Digital Out PWM Battery Diversion (Active Low)
    2:  "WASTE NOT HIGH",           # Digital Out PWM relative to Charge Stage Voltage Threshold Diversion (Use It Or Lose It) (Active High)
    3:  "WASTE NOT LOW",            # Digital Out PWM relative to Charge Stage Voltage Threshold Diversion (Use It Or Lose It) (Active Low)
    4:  "RESERVED",                 # Unimplemented
    5:  "RESERVED",                 # Unimplemented
    6:  "TOGGLE TEST",              # Out once per second On-Off-On-Off automatic toggle
    7:  "PV V ON HIGH",             # Active High output if Vin exceeds Aux2VoltsHiPv
    8:  "PV V ON LOW",              # Active Low output if Vin exceeds Aux2VoltsHiPv
    9:  "RESERVED",                 # Unimplemented
    10: "WIND CLIPPER CONTROL",     # PWM output Active High when Vin is above PV input V plus headroom voltage
    11: "NIGHT LIGHT HIGH",         # Active High On at Dawn, Off at Dusk
    12: "DAY LIGHT HIGH",           # Active High Off at Dawn, On at Dusk
    13: "FLOAT HIGH OUTPUT",        # Active High output when Float stage is reached
    14: "FLOAT LOW OUTPUT",         # Active Low output when Float stage is reached
    15: "Active HIGH (input) turn off",  # > 6.0 V into Aux 2 forces Classic to resting (15 V max)
    16: "Active LOW (input) turn off",   # < 2.0 V into Aux 2 forces Classic to resting (0 V min)
    17: "Active HIGH (input) Float",     # > 6.0 V into Aux 2 forces Classic to Float (15 V max)
    18: "Whizbang Junior (WB Jr.)",      # Aux 2 commands WB Jr. and receives info from WB Jr.
}

# Table 4164-1 — MPPT Mode (register 4164)
# "Bit 0 is the ON/OFF (Enable/Disable). Table shows modes as ON —
#  subtract one (1) if showing mode as OFF."
# Both the ON (odd) and OFF (even) encodings are mapped so the text stays
# meaningful when the MPPT controller is switched off (see switch.py).
MPPT_MODE_TEXT = {
    0x0000: "PV_Uset",      0x0001: "PV_Uset",      # U-SET MPPT mode
    0x0002: "DYNAMIC",      0x0003: "DYNAMIC",      # Slow Dynamic Solar Tracking (old Solar 1 O&P)
    0x0004: "WIND TRACK",   0x0005: "WIND TRACK",   # Wind Track mode
    0x0006: "RESERVED",     0x0007: "RESERVED",     # Reserved for future Wind Learn mode
    0x0008: "Legacy P&O",   0x0009: "Legacy P&O",   # Legacy P&O sweep mode
    0x000A: "SOLAR",        0x000B: "SOLAR",        # Fast SOLAR track (old PV Learn mode)
    0x000C: "HYDRO",        0x000D: "HYDRO",        # Micro Hydro mode (similar to Legacy P&O)
    0x000E: "RESERVED",     0x000F: "RESERVED",     # RESERVED
}

# Table 4275-1 — Reason For Resting (register 4275)
# Descriptions are reproduced verbatim from the manufacturer documentation.
# Values 104 and 111 are not in the spec but are observed in the field.
REASON_FOR_RESTING_TEXT = {
    1:  "Anti-Click. Not enough power available (Wake Up)",
    2:  "Insane Ibatt Measurement (Wake Up)",
    3:  "Negative Current (load on PV input ?) (Wake Up)",
    4:  "PV Input Voltage lower than Battery V (Vreg state)",
    5:  "Too low of power out and Vbatt below set point for > 90 seconds",
    6:  "FET temperature too high (Cover is on maybe?)",
    7:  "Ground Fault Detected",
    8:  "Arc Fault Detected",
    9:  "Too much negative current while operating (backfeed from battery out of PV input)",
    10: "Battery is less than 8.0 Volts",
    11: "PV input is available but V is rising too slowly. Low Light or bad connection (Solar mode)",
    12: "Voc has gone down from last Voc or low light. Re-check (Solar mode)",
    13: "Voc has gone up from last Voc enough to be suspicious. Re-check (Solar mode)",
    14: "PV input is available but V is rising too slowly. Low Light or bad connection (Solar mode)",
    15: "Voc has gone down from last Voc or low light. Re-check (Solar mode)",
    16: "Mppt MODE is OFF (Usually because user turned it off)",
    17: "PV input is higher than operation range (too high for 150V Classic)",
    18: "PV input is higher than operation range (too high for 200V Classic)",
    19: "PV input is higher than operation range (too high for 250V or 250KS)",
    22: "Average Battery Voltage is too high above set point",
    25: "Battery Voltage too high of Overshoot (small battery or bad cable ?)",
    26: "Mode changed while running OR Vabsorb raised more than 10.0 Volts at once OR "
        "Nominal Vbatt changed by modbus command AND MpptMode was ON when changed",
    27: "bridge center == 1023 (R132 might have been stuffed) This turns MPPT Mode to OFF",
    28: "NOT Resting but RELAY is not engaged for some reason",
    29: "ON/OFF stays off because WIND GRAPH is illegal (current step is set for > 100 amps)",
    30: "PkAmpsOverLimit... Software detected too high of PEAK output current",
    31: "AD1CH.IbattMinus > 900 Peak negative battery current > 90.0 amps (Classic 250)",
    32: "Aux 2 input commanded Classic off. for HI or LO (Aux2Function == 15 or 16)",
    33: "OCP in a mode other than Solar or PV-Uset",
    34: "AD1CH.IbattMinus > 900 Peak negative battery current > 90.0 amps (Classic 150, 200)",
    35: "Battery voltage is less than Low Battery Disconnect (LBD) Typically Vbatt is less than 8.5 volts",
    104: "104?=14?: PV input is available but V is rising too slowly. Low Light or bad connection (Solar mode)",
    111: "Normal Power up boot.",
}

# Home Assistant refuses to store a state longer than 255 characters.
MAX_STATE_LENGTH = 255


def _lookup(table: dict, value, label: str, host: str = "") -> str:
    """Return table[value], logging a warning and falling back to a readable
    placeholder when the value is not documented.

    The fallback wording is kept identical to the original standalone script so
    that unknown codes stay recognisable in the logs and in the HA UI.
    """
    try:
        text = table[value]
    except KeyError:
        log.warning(
            "%s: undefined value %s%s",
            label,
            value,
            f" for host {host}" if host else "",
        )
        return f"No text defined for this value...{value}"

    if len(text) > MAX_STATE_LENGTH:
        text = text[: MAX_STATE_LENGTH - 1] + "\u2026"
    return text


# --------------------------------------------------------------------------- #
# Based on the address, return the decoded OrderedDict
#
# Note that the starting address is the target starting register address minus 1.
# Excerpt from the Midnite Classic MODBUS protocol manual:
# Note on addresses vs. registers:
# The modbus specification adds one (1) to the “address” sent to the unit in the packet command to access a “register”. This is
# so that modbus registers start at 1 rather than 0. The main Classic address map starts at register 4101 but the packet itself
# sends out address 4100.
# Some modbus software and libraries will go by register number and some will go by address so make sure which one it works
# with.
# --------------------------------------------------------------------------- #


def doDecode(addr, decoder):
    if addr == 4100:
        decoded = OrderedDict(
            [
                ("PCB", decoder.decode_8bit_uint()),  # 4101 MSB
                ("Type", decoder.decode_8bit_uint()),  # 4101 LSB
                ("Year", decoder.decode_16bit_uint()),  # 4102
                ("Month", decoder.decode_8bit_uint()),  # 4103 MSB
                ("Day", decoder.decode_8bit_uint()),  # 4103 LSB
                ("InfoFlagBits3", decoder.decode_16bit_uint()),  # 4104
                ("ignore", decoder.skip_bytes(2)),  # 4105 Reserved
                ("mac_1", decoder.decode_8bit_uint()),  # 4106 MSB
                ("mac_0", decoder.decode_8bit_uint()),  # 4106 LSB
                ("mac_3", decoder.decode_8bit_uint()),  # 4107 MSB
                ("mac_2", decoder.decode_8bit_uint()),  # 4107 LSB
                ("mac_5", decoder.decode_8bit_uint()),  # 4108 MSB
                ("mac_4", decoder.decode_8bit_uint()),  # 4108 LSB
                ("ignore2", decoder.skip_bytes(4)),  # 4109, 4110
                ("unitID", decoder.decode_32bit_uint()),  # 4111
                ("StatusRoll", decoder.decode_16bit_uint()),  # 4113
                ("RsetTmms", decoder.decode_16bit_uint()),  # 4114
                ("BatVoltage", decoder.decode_16bit_int() / 10.0),  # 4115
                ("PVVoltage", decoder.decode_16bit_uint() / 10.0),  # 4116
                ("BatCurrent", decoder.decode_16bit_uint() / 10.0),  # 4117
                ("EnergyToday", decoder.decode_16bit_uint() / 10.0),  # 4118
                ("Power", decoder.decode_16bit_uint() / 1.0),  # 4119
                ("ChargeStage", decoder.decode_8bit_uint()),  # 4120 MSB
                ("State", decoder.decode_8bit_uint()),  # 4120 LSB
                ("PVCurrent", decoder.decode_16bit_uint() / 10.0),  # 4121
                ("lastVOC", decoder.decode_16bit_uint() / 10.0),  # 4122
                ("HighestVinputLog", decoder.decode_16bit_uint()),  # 4123
                ("MatchPointShadow", decoder.decode_16bit_uint()),  # 4124
                ("AmpHours", decoder.decode_16bit_uint()),  # 4125
                ("TotalEnergy", decoder.decode_32bit_uint() / 10.0),  # 4126, 4127
                ("LifetimeAmpHours", decoder.decode_32bit_uint()),  # 4128, 4129
                ("InfoFlagsBits", decoder.decode_32bit_uint()),  # 4130, 31
                ("BatTemperature", decoder.decode_16bit_int() / 10.0),  # 4132
                ("FETTemperature", decoder.decode_16bit_int() / 10.0),  # 4133
                ("PCBTemperature", decoder.decode_16bit_int() / 10.0),  # 4134
                ("NiteMinutesNoPwr", decoder.decode_16bit_uint()),  # 4135
                ("MinuteLogIntervalSec", decoder.decode_16bit_uint()),  # 4136
                ("modbus_port_register", decoder.decode_16bit_uint()),  # 4137
                ("FloatTimeTodaySeconds", decoder.decode_16bit_uint()),  # 4138
                ("AbsorbTime", decoder.decode_16bit_uint()),  # 4139
                ("reserved1", decoder.decode_16bit_uint()),  # 4140
                ("PWM_ReadOnly", decoder.decode_16bit_uint()),  # 4141
                ("Reason_For_Reset", decoder.decode_16bit_uint()),  # 4142
                ("EqualizeTime", decoder.decode_16bit_uint()),  # 4143
            ]
        )
    elif addr == 4148:
        decoded = OrderedDict(
            [
                ("AbsorbVoltageSetPoint", decoder.decode_16bit_int() / 10.0),  # 4149
                ("FloatVoltageSetPoint", decoder.decode_16bit_int() / 10.0),  # 4150
                ("EqualizeVoltageSetPoint", decoder.decode_16bit_int() / 10.0),  # 4151
            ]
        )
    elif addr == 4360:
        decoded = OrderedDict(
            [
                ("WbangJrCmdS", decoder.decode_16bit_uint()),  # 4361
                ("WizBangJrRawCurrent", decoder.decode_16bit_int() / 10.0),  # 4362
                ("skip", decoder.skip_bytes(4)),  # 4363,4364
                ("WbJrAmpHourPOSitive", decoder.decode_32bit_uint()),  # 4365,4366
                ("WbJrAmpHourNEGative", decoder.decode_32bit_int()),  # 4367,4368
                ("WbJrAmpHourNET", decoder.decode_32bit_int()),  # 4369,4370
                ("WhizbangBatCurrent", decoder.decode_16bit_int() / 10.0),  # 4371
                ("WizBangCRC", decoder.decode_8bit_int()),  # 4372 MSB
                ("ShuntTemperature", decoder.decode_8bit_int() - 50.0),  # 4372 LSB
                ("SOC", decoder.decode_16bit_uint()),  # 4373
                ("skip2", decoder.skip_bytes(6)),  # 4374,75, 76
                ("RemainingAmpHours", decoder.decode_16bit_uint()),  # 4377
                ("skip3", decoder.skip_bytes(6)),  # 4378,79,80
                ("TotalAmpHours", decoder.decode_16bit_uint()),  # 4381
            ]
        )
    elif addr == 4161:
        decoded = OrderedDict(
            [
                ("EqualizeTimeSetPoint", decoder.decode_16bit_uint()),  # 4162
                ("EqualizeIntervalDay", decoder.decode_16bit_uint()),  # 4163
                ("MPPTMode", decoder.decode_16bit_uint()),  # 4164
                ("Aux12Function", decoder.decode_16bit_uint()),  # 4165
            ]
        )
    elif addr == 4209:
        decoded = OrderedDict(
            [
                ("Name0", decoder.decode_8bit_uint()),  # 4210-MSB
                ("Name1", decoder.decode_8bit_uint()),  # 4210-LSB
                ("Name2", decoder.decode_8bit_uint()),  # 4211-MSB
                ("Name3", decoder.decode_8bit_uint()),  # 4211-LSB
                ("Name4", decoder.decode_8bit_uint()),  # 4212-MSB
                ("Name5", decoder.decode_8bit_uint()),  # 4212-LSB
                ("Name6", decoder.decode_8bit_uint()),  # 4213-MSB
                ("Name7", decoder.decode_8bit_uint()),  # 4213-LSB
            ]
        )
    elif addr == 4213:
        decoded = OrderedDict(
            [
                ("CTIME0", decoder.decode_32bit_uint()),  # 4214+#4215
                ("CTIME1", decoder.decode_32bit_uint()),  # 4216+#4217
                ("CTIME2", decoder.decode_32bit_uint()),  # 4218+#4219
            ]
        )
    elif addr == 4243:
        decoded = OrderedDict(
            [
                ("VbattRegSetPTmpComp", decoder.decode_16bit_int() / 10.0),  # 4244
                ("nominalBatteryVoltage", decoder.decode_16bit_uint()),  # 4245
                ("endingAmps", decoder.decode_16bit_int() / 10.0),  # 4246
                ("skip", decoder.skip_bytes(56)),  # 4247-4274
                ("ReasonForResting", decoder.decode_16bit_uint()),  # 4275
            ]
        )
    elif addr == 4251:
        decoded = OrderedDict(
            [
                ("DaysBetweenBulkAbsorb", decoder.decode_16bit_int()),  # 4252
            ]
        )
    elif addr == 16386:
        decoded = OrderedDict(
            [
                ("app_rev", decoder.decode_32bit_uint()),  # 16387, 16388
                ("net_rev", decoder.decode_32bit_uint()),  # 16387, 16388
            ]
        )
    else:
        log.warning(f"doDecode: adresse inconnue {addr} — ignorée")
        return {}   # retourne dict vide plutôt que planter

    return decoded


# --------------------------------------------------------------------------- #
# Public entry point for the HA integration
# Opens a fresh Modbus connection, reads all registers, closes it, returns dict
# --------------------------------------------------------------------------- #
def getRegisters(ip: str, port: int = 502) -> dict:
    """Connect to the Classic, read all registers and return a decoded dict.

    This is called by classic_reader.py in a thread-pool executor.
    A new TCP connection is opened and closed on every call (stateless).
    """
    client = ModbusClient(host=ip, port=port)
    try:
        client.connect()

        # Quick sanity check
        probe = client.read_holding_registers(4163, count=2)
        if probe.isError():
            log.error(f"Modbus probe failed for {ip}:{port}")
            return {}

        raw = {}
        raw[4100]  = _readRegisters(client, 4100,  44)
        raw[4360]  = _readRegisters(client, 4360,  22)
        raw[4148]  = _readRegisters(client, 4148,   3)
        raw[4161]  = _readRegisters(client, 4161,   4)
        raw[4209]  = _readRegisters(client, 4209,   4)
        raw[4213]  = _readRegisters(client, 4213,   6)
        raw[4243]  = _readRegisters(client, 4243,  32)
        raw[4251]  = _readRegisters(client, 4251,   1)
        raw[16386] = _readRegisters(client, 16386,  4)

    except Exception as ex:
        log.error(f"Modbus error {ip}:{port} — {ex}")
        return {}
    finally:
        client.close()

    # Decode all register blocks into one flat dict
    decoded: dict = {}
    for addr, registers in raw.items():
        if registers:
            decoded.update(doDecode(addr, getDataDecoder(registers)))

    if not decoded:
        return {}

    # ------------------------------------------------------------------ #
    # Post-processing — identical to original getModbusData()
    # ------------------------------------------------------------------ #

    if decoded.get("Type") == 251:
        decoded["Type"] = "250 KS"

    decoded["IP"] = ip
    decoded["MAC"] = ":".join(
        f"{octet:02X}"
        for octet in (
            decoded.get("mac_5", 0), decoded.get("mac_4", 0),
            decoded.get("mac_3", 0), decoded.get("mac_2", 0),
            decoded.get("mac_1", 0), decoded.get("mac_0", 0),
        )
    )
    decoded["Name"] = "".join(
        chr(c) for c in (
            decoded.get("Name1", 0), decoded.get("Name0", 0),
            decoded.get("Name3", 0), decoded.get("Name2", 0),
            decoded.get("Name5", 0), decoded.get("Name4", 0),
            decoded.get("Name7", 0), decoded.get("Name6", 0),
        )
    ).strip("\x00").strip()

    # Charge state
    stage = decoded.get("ChargeStage", 0)
    if stage in (3, 4):
        decoded["ChargeStateIcon"] = "mdi:battery-charging"
    elif stage in (5, 6):
        decoded["ChargeStateIcon"] = "mdi:format-float-center"
    elif stage >= 7:
        decoded["ChargeStateIcon"] = "mdi:approximately-equal"
    else:
        decoded["ChargeStateIcon"] = "mdi:music-rest-whole"

    decoded["ChargeStateText"] = _lookup(
        CHARGE_STAGE_TEXT, stage, "ChargeStateText", ip
    )

    # ------------------------------------------------------------------ #
    # AUX 1 / AUX 2 — register 4165 (Aux12Function), Tables 4165-1 … 4165-4
    #   AUX 1 Off-Auto-On : bits 6,7    Aux1OffAutoOn = (Aux12Function & 0xC0) >> 6
    #   AUX 1 Function    : bits 0-5    Aux1Function  =  Aux12Function & 0x3F
    #   AUX 2 Off-Auto-On : bits 14,15  Aux2OffAutoOn = (Aux12Function & 0xC000) >> 14
    #   AUX 2 Function    : bits 8-13   Aux2Function  = (Aux12Function & 0x3F00) >> 8
    # ------------------------------------------------------------------ #
    aux12 = decoded.get("Aux12Function", 0)

    decoded["Aux1OffAutoOn"] = (aux12 & 0xC0) >> 6
    decoded["Aux1Function"] = aux12 & 0x3F
    decoded["Aux2OffAutoOn"] = (aux12 & 0xC000) >> 14
    decoded["Aux2Function"] = (aux12 & 0x3F00) >> 8

    decoded["Aux1FunctionText"] = _lookup(
        AUX1_FUNCTION_TEXT, decoded["Aux1Function"], "Aux1FunctionText", ip
    )
    decoded["Aux1OffAutoOnText"] = _lookup(
        AUX_OFF_AUTO_ON, decoded["Aux1OffAutoOn"], "Aux1OffAutoOnText", ip
    )
    decoded["Aux2FunctionText"] = _lookup(
        AUX2_FUNCTION_TEXT, decoded["Aux2Function"], "Aux2FunctionText", ip
    )
    decoded["Aux2OffAutoOnText"] = _lookup(
        AUX_OFF_AUTO_ON, decoded["Aux2OffAutoOn"], "Aux2OffAutoOnText", ip
    )

    # MPPT mode — Table 4164-1 (bit 0 = ON/OFF, handled by switch.py)
    decoded["MPPTModeText"] = _lookup(
        MPPT_MODE_TEXT, decoded.get("MPPTMode"), "MPPTModeText", ip
    )

    # SOC icon
    soc_icon = "mdi:battery-"
    if stage in (3, 4):
        soc_icon += "charging-"
    soc_icon += str(int(int(decoded.get("SOC", 0)) / 10)) + "0"
    if soc_icon == "mdi:battery-100":
        soc_icon = "mdi:battery"
    decoded["SOCicon"] = soc_icon

    # Reason for resting — Table 4275-1
    decoded["ReasonForRestingText"] = _lookup(
        REASON_FOR_RESTING_TEXT,
        decoded.get("ReasonForResting"),
        "ReasonForRestingText",
        ip,
    )

    return decoded