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
                ("EqualiseIntervalDay", decoder.decode_16bit_uint()),  # 4163
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

    chrg_stt_txt = {
        0: "Resting", 3: "Absorb", 4: "Bulk MPPT",
        5: "Float", 6: "Float MPPT", 7: "Equalize",
        10: "HyperVOC", 18: "Equalize MPPT",
    }
    decoded["ChargeStateText"] = chrg_stt_txt.get(
        stage, f"Unknown ({stage})"
    )

    # AUX
    aux12 = decoded.get("Aux12Function", 0)
    decoded["Aux1OffAutoOn"] = (aux12 & 0xC0) >> 6
    decoded["Aux1Function"]  = aux12 & 0x3F
    decoded["Aux2OffAutoOn"] = (aux12 & 0xC000) >> 14
    decoded["Aux2Function"]  = (aux12 & 0x3F00) >> 8

    aux_oa = {0: "AUX Off", 1: "AUX Auto", 2: "AUX On", 3: "Unimplemented"}
    decoded["Aux1OffAutoOnText"] = aux_oa.get(decoded["Aux1OffAutoOn"], str(decoded["Aux1OffAutoOn"]))
    decoded["Aux2OffAutoOnText"] = aux_oa.get(decoded["Aux2OffAutoOn"], str(decoded["Aux2OffAutoOn"]))

    # MPPT mode
    mppt_mode = {
        1: "PV_Uset", 3: "DYNAMIC", 5: "WIND TRACK", 7: "RESERVED",
        9: "Legacy P&O", 11: "SOLAR", 13: "HYDRO", 15: "RESERVED",
    }
    decoded["MPPTModeText"] = mppt_mode.get(
        decoded.get("MPPTMode"), f"Unknown ({decoded.get('MPPTMode')})"
    )

    # SOC icon
    soc_icon = "mdi:battery-"
    if stage in (3, 4):
        soc_icon += "charging-"
    soc_icon += str(int(int(decoded.get("SOC", 0)) / 10)) + "0"
    if soc_icon == "mdi:battery-100":
        soc_icon = "mdi:battery"
    decoded["SOCicon"] = soc_icon

    # Reason for resting
    rest_reason = {
        1: "Anti-Click — not enough power (Wake Up)",
        2: "Insane Ibatt measurement (Wake Up)",
        3: "Negative current — load on PV? (Wake Up)",
        4: "PV voltage lower than battery voltage (Vreg)",
        5: "Too low power, Vbatt below setpoint >90s",
        6: "FET temperature too high",
        7: "Ground fault detected",
        8: "Arc fault detected",
        9: "Too much negative current",
        10: "Battery < 8.0 V",
        11: "PV voltage rising too slowly (Solar)",
        12: "Voc decreased from last Voc (Solar)",
        13: "Voc increased suspiciously (Solar)",
        16: "MPPT mode OFF",
        17: "PV input too high (150V Classic)",
        18: "PV input too high (200V Classic)",
        19: "PV input too high (250V Classic)",
        22: "Average battery voltage too high",
        25: "Battery voltage overshoot",
        26: "Mode changed while running",
        27: "Bridge centre == 1023",
        28: "Not resting but relay not engaged",
        29: "Wind graph illegal",
        30: "Peak output current too high",
        31: "Peak negative battery current > 90A (250)",
        32: "Aux2 commanded Classic off",
        33: "OCP in non-Solar mode",
        34: "Peak negative battery current > 90A (150/200)",
        35: "Battery below Low Battery Disconnect",
        104: "PV rising too slowly (Solar)",
        111: "Normal power-up boot",
    }
    idx = decoded.get("ReasonForResting", 0)
    decoded["ReasonForRestingText"] = rest_reason.get(idx, f"Unknown code: {idx}")

    return decoded


