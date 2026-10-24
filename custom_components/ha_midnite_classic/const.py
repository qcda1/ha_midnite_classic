"""Constants for the Midnite Solar Classic integration."""

DOMAIN = "ha_midnite_classic"
VERSION = "1.4.0"

# Config entry keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_MONITORED_PARAMETERS = "monitored_parameters"

# Defaults
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 60  # seconds
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 3600

# Default parameters selected at installation
DEFAULT_PARAMETERS = [
    "BatVoltage",
    "PVVoltage",
    "BatCurrent",
    "EnergyToday",
    "Power",
    "ChargeStage",
    "State",
    "PVCurrent",
    "TotalEnergy",
    "Name",
    "ChargeStateText",
]

# All known parameters from classic_modbusdecoder with metadata
# Format: key -> (friendly_name, unit, device_class_str, state_class_str, icon,
#                 precision, writable, min_val, max_val, step, scale)
#
# precision : int   — nb of decimal digits for HA display (0 = integer)
# writable  : bool  — True = exposed as a number entity (editable)
# min_val   : float | int | None — minimum value in HA units
# max_val   : float | int | None — maximum value in HA units
# step      : float | int | None — step in HA units
# scale     : int | None         — multiply HA value by scale before writing to Modbus
#                                  (e.g. 10 for voltages stored as V×10, 1 for integers)
PARAMETER_META: dict[str, tuple] = {
    "PCB":                     ("PCB Version",               None,  None,          None,                 "mdi:chip",                        0, False, None, None, None, None),
    "Type":                    ("Controller Type",           None,  None,          None,                 "mdi:solar-power",                 0, False, None, None, None, None),
    "Year":                    ("Firmware Year",             None,  None,          None,                 "mdi:calendar",                    0, False, None, None, None, None),
    "Month":                   ("Firmware Month",            None,  None,          None,                 "mdi:calendar",                    0, False, None, None, None, None),
    "Day":                     ("Firmware Day",              None,  None,          None,                 "mdi:calendar",                    0, False, None, None, None, None),
    "InfoFlagBits3":           ("Info Flag Bits 3",          None,  None,          None,                 "mdi:flag",                        0, False, None, None, None, None),
    "mac_0":                   ("MAC Byte 0",                None,  None,          None,                 "mdi:ethernet",                    0, False, None, None, None, None),
    "mac_1":                   ("MAC Byte 1",                None,  None,          None,                 "mdi:ethernet",                    0, False, None, None, None, None),
    "mac_2":                   ("MAC Byte 2",                None,  None,          None,                 "mdi:ethernet",                    0, False, None, None, None, None),
    "mac_3":                   ("MAC Byte 3",                None,  None,          None,                 "mdi:ethernet",                    0, False, None, None, None, None),
    "mac_4":                   ("MAC Byte 4",                None,  None,          None,                 "mdi:ethernet",                    0, False, None, None, None, None),
    "mac_5":                   ("MAC Byte 5",                None,  None,          None,                 "mdi:ethernet",                    0, False, None, None, None, None),
    "unitID":                  ("Unit ID",                   None,  None,          None,                 "mdi:identifier",                  0, False, None, None, None, None),
    "StatusRoll":              ("Status Roll",               None,  None,          None,                 "mdi:information",                 0, False, None, None, None, None),
    "RsetTmms":                ("Reset Time ms",             "ms",  None,          None,                 "mdi:timer",                       0, False, None, None, None, None),
    "BatVoltage":              ("Battery Voltage",           "V",   "voltage",     "measurement",        "mdi:battery",                     1, False, None, None, None, None),
    "PVVoltage":               ("PV Voltage",                "V",   "voltage",     "measurement",        "mdi:solar-panel",                 1, False, None, None, None, None),
    "BatCurrent":              ("Battery Current",           "A",   "current",     "measurement",        "mdi:current-dc",                  1, False, None, None, None, None),
    "EnergyToday":             ("Energy Today",              "kWh", "energy",      "total_increasing",   "mdi:calendar-today",              0, False, None, None, None, None),
    "Power":                   ("Power",                     "W",   "power",       "measurement",        "mdi:flash",                       0, False, None, None, None, None),
    "ChargeStage":             ("Charge Stage",              None,  None,          None,                 "mdi:battery-charging",            0, False, None, None, None, None),
    "State":                   ("State",                     None,  None,          None,                 "mdi:state-machine",               0, False, None, None, None, None),
    "PVCurrent":               ("PV Current",                "A",   "current",     "measurement",        "mdi:current-dc",                  1, False, None, None, None, None),
    "lastVOC":                 ("Last VOC",                  "V",   "voltage",     "measurement",        "mdi:solar-panel",                 1, False, None, None, None, None),
    "HighestVinputLog":        ("Highest Vin Log",           None,  None,          None,                 "mdi:chart-line",                  0, False, None, None, None, None),
    "MatchPointShadow":        ("Match Point Shadow",        None,  None,          None,                 "mdi:weather-cloudy",              0, False, None, None, None, None),
    "AmpHours":                ("Amp Hours",                 "Ah",  None,          "total_increasing",   "mdi:battery-charging",            0, False, None, None, None, None),
    "TotalEnergy":             ("Total Energy",              "kWh", "energy",      "total_increasing",   "mdi:lightning-bolt",              0, False, None, None, None, None),
    "LifetimeAmpHours":        ("Lifetime Amp Hours",        "Ah",  None,          "total_increasing",   "mdi:battery-high",                0, False, None, None, None, None),
    "InfoFlagsBits":           ("Info Flags Bits",           None,  None,          None,                 "mdi:flag-variant",                0, False, None, None, None, None),
    "BatTemperature":          ("Battery Temperature",       "°C",  "temperature", "measurement",        "mdi:thermometer",                 1, False, None, None, None, None),
    "FETTemperature":          ("FET Temperature",           "°C",  "temperature", "measurement",        "mdi:thermometer",                 1, False, None, None, None, None),
    "PCBTemperature":          ("PCB Temperature",           "°C",  "temperature", "measurement",        "mdi:thermometer",                 1, False, None, None, None, None),
    "NiteMinutesNoPwr":        ("Night Minutes No Power",    "min", None,          "measurement",        "mdi:weather-night",               0, False, None, None, None, None),
    "MinuteLogIntervalSec":    ("Log Interval",              "s",   None,          None,                 "mdi:timer",                       0, False, None, None, None, None),
    "modbus_port_register":    ("Modbus Port",               None,  None,          None,                 "mdi:lan",                         0, False, None, None, None, None),
    "FloatTimeTodaySeconds":   ("Float Time Today",          "s",   None,          "measurement",        "mdi:timer",                       0, False, None, None, None, None),
    "AbsorbTime":              ("Absorb Time",               "s",   None,          None,                 "mdi:timer",                       0, False, None, None, None, None),
    "PWM_ReadOnly":            ("PWM",                       None,  None,          "measurement",        "mdi:pulse",                       0, False, None, None, None, None),
    "Reason_For_Reset":        ("Reason For Reset",          None,  None,          None,                 "mdi:restart",                     0, False, None, None, None, None),
    "EqualizeTime":            ("Equalize Time",             "s",   None,          None,                 "mdi:timer",                       0, False, None, None, None, None),
    "WbangJrCmdS":             ("WhizBang Jr Command",       None,  None,          None,                 "mdi:remote",                      0, False, None, None, None, None),
    "WizBangJrRawCurrent":     ("WhizBang Jr Raw Current",   "A",   "current",     "measurement",        "mdi:current-dc",                  0, False, None, None, None, None),
    "Name":                    ("Device Name",               None,  None,          None,                 "mdi:tag",                         0, False, None, None, None, None),
    "ChargeStateText":         ("Charge State Text",         None,  None,          None,                 "mdi:battery-charging-outline",    0, False, None, None, None, None),
    "MPPTMode":                ("MPPT Mode",                 None,  None,          None,                 "mdi:sun-wireless",                0, False, None, None, None, None),
    "endingAmps":              ("Absorb End Amps",           "A",   "current",     None,                 "mdi:current-dc",                  1, True,     0, 20,  0.1,   10),
    "ReasonForResting":        ("Reason For Resting",        None,  None,          None,                 "mdi:sleep",                       0, False, None, None, None, None),
    # --- WhizBang Jr. / battery monitor (registers 4361-4381) ---
    "SOC":                     ("State Of Charge",           "%",   "battery",     "measurement",        "mdi:battery-heart-variant",       0, False, None, None, None, None),
    "RemainingAmpHours":       ("Remaining Amp Hours",       "Ah",  None,          "measurement",        "mdi:battery-clock",               0, False, None, None, None, None),
    "TotalAmpHours":           ("Total Amp Hours",           "Ah",  None,          None,                 "mdi:battery",                     0, False, None, None, None, None),
    "WhizbangBatCurrent":      ("WhizBang Battery Current",  "A",   "current",     "measurement",        "mdi:current-dc",                  1, False, None, None, None, None),
    "ShuntTemperature":        ("Shunt Temperature",         "°C",  "temperature", "measurement",        "mdi:thermometer",                 0, False, None, None, None, None),
    "WbJrAmpHourPOSitive":     ("WBJr Amp Hours Positive",   "Ah",  None,          "total_increasing",   "mdi:battery-plus",                0, False, None, None, None, None),
    "WbJrAmpHourNEGative":     ("WBJr Amp Hours Negative",   "Ah",  None,          None,                 "mdi:battery-minus",               0, False, None, None, None, None),
    "WbJrAmpHourNET":          ("WBJr Amp Hours Net",        "Ah",  None,          "measurement",        "mdi:battery-sync",                0, False, None, None, None, None),
    # --- AUX 1 / AUX 2 decoded from register 4165 (Aux12Function) ---
    "Aux12Function":           ("Aux 1&2 Function (raw)",    None,  None,          None,                 "mdi:electric-switch",             0, False, None, None, None, None),
    "Aux1Function":            ("Aux 1 Function",            None,  None,          None,                 "mdi:electric-switch",             0, False, None, None, None, None),
    "Aux1FunctionText":        ("Aux 1 Function Text",       None,  None,          None,                 "mdi:electric-switch",             0, False, None, None, None, None),
    "Aux1OffAutoOn":           ("Aux 1 Off/Auto/On",         None,  None,          None,                 "mdi:toggle-switch",               0, False, None, None, None, None),
    "Aux1OffAutoOnText":       ("Aux 1 Off/Auto/On Text",    None,  None,          None,                 "mdi:toggle-switch",               0, False, None, None, None, None),
    "Aux2Function":            ("Aux 2 Function",            None,  None,          None,                 "mdi:electric-switch",             0, False, None, None, None, None),
    "Aux2FunctionText":        ("Aux 2 Function Text",       None,  None,          None,                 "mdi:electric-switch",             0, False, None, None, None, None),
    "Aux2OffAutoOn":           ("Aux 2 Off/Auto/On",         None,  None,          None,                 "mdi:toggle-switch",               0, False, None, None, None, None),
    "Aux2OffAutoOnText":       ("Aux 2 Off/Auto/On Text",    None,  None,          None,                 "mdi:toggle-switch",               0, False, None, None, None, None),
    # --- Decoded text helpers ---
    "MPPTModeText":            ("MPPT Mode Text",            None,  None,          None,                 "mdi:sun-wireless",                0, False, None, None, None, None),
    "ReasonForRestingText":    ("Reason For Resting Text",   None,  None,          None,                 "mdi:sleep",                       0, False, None, None, None, None),
    # --- Misc device information ---
    "VbattRegSetPTmpComp":     ("Vbatt Reg Setpoint (TC)",   "V",   "voltage",     "measurement",        "mdi:battery-lock",                1, False, None, None, None, None),
    "nominalBatteryVoltage":   ("Nominal Battery Voltage",   "V",   "voltage",     None,                 "mdi:battery",                     0, False, None, None, None, None),
    "app_rev":                 ("Application Revision",      None,  None,          None,                 "mdi:numeric",                     0, False, None, None, None, None),
    "net_rev":                 ("Network Revision",          None,  None,          None,                 "mdi:numeric",                     0, False, None, None, None, None),
    "IP":                      ("IP Address",                None,  None,          None,                 "mdi:ip-network",                  0, False, None, None, None, None),
    "MAC":                     ("MAC Address",               None,  None,          None,                 "mdi:ethernet",                    0, False, None, None, None, None),
    # --- AUX 1 control registers (4166-4172) — all marked (EE) in the manual ---
    # Units confirmed by bench testing against the MNGP console (Classic 150):
    #   4166 / 4172  thresholds — raw percent when Aux1Function is SOC% HIGH/LOW
    #                (22/23). Register 94 displays as 94, so no /10 is applied.
    #                In a voltage AUX 1 mode the manual's ([reg] / 10) Volts
    #                applies instead; change unit to "V" and scale to 10.
    #   4167 / 4168  timings — TENTHS of a second, not milliseconds as the manual
    #                states. Verified over three generator transitions: 300 -> 30 s,
    #                600 -> 60 s, 6000 -> 10 min.
    "Aux1VoltsLoAbs":          ("Aux 1 Low Threshold",       "%",   None,          "measurement",        "mdi:arrow-down-bold-box",         0, True,     0,    100,   1,    1),
    "Aux1VoltsHiAbs":          ("Aux 1 High Threshold",      "%",   None,          "measurement",        "mdi:arrow-up-bold-box",           0, True,     0,    100,   1,    1),
    "Aux1DelayT":              ("Aux 1 Delay Time",          "s",   "duration",    "measurement",        "mdi:timer-play",                  1, True,     0, 6553.5, 0.1,  10),
    "Aux1HoldT":               ("Aux 1 Hold Time",           "s",   "duration",    "measurement",        "mdi:timer-stop",                  1, True,     0, 6553.5, 0.1,  10),
    "Aux2PwmVwidth":           ("Aux 2 PWM Voltage Width",   None,  None,          None,                 "mdi:pulse",                       0, False, None, None, None, None),
    # --- Writable setpoints (number entities) ---
    # Modbus register numbers (not addresses): H4149–H4151, H4162, H4163, H4252
    # Address sent to device = register - 1 (per Modbus spec / Classic manual)
    "AbsorbVoltageSetPoint":   ("Absorb Voltage Setpoint",   "V",   "voltage",     "measurement",        "mdi:solar-panel",                 1, True,  10.0, 65.0, 0.1, 10),
    "FloatVoltageSetPoint":    ("Float Voltage Setpoint",    "V",   "voltage",     "measurement",        "mdi:solar-panel",                 1, True,  10.0, 65.0, 0.1, 10),
    "EqualizeVoltageSetPoint": ("Equalize Voltage Setpoint", "V",   "voltage",     "measurement",        "mdi:solar-panel",                 1, True,  10.0, 65.0, 0.1, 10),
    "EqualizeTimeSetPoint":    ("Equalize Time Setpoint",    "s",   None,          None,                 "mdi:timer",                       0, True,  0,   14400,   1,  1),
    "EqualizeIntervalDay":     ("Equalize Interval Day",     "day", None,          None,                 "mdi:numeric",                     0, True,  0,     255,   1,  1),
    "DaysBetweenBulkAbsorb":   ("Days Between Bulk/Absorb",  "day", None,          None,                 "mdi:numeric",                     0, True,  0,     255,   1,  1),
}

# Modbus register numbers for writable setpoints (address = register - 1)
# Per Classic manual note: packet sends address = register - 1
WRITABLE_REGISTERS: dict[str, int] = {
    "endingAmps":              4246,
    "AbsorbVoltageSetPoint":   4149,
    "FloatVoltageSetPoint":    4150,
    "EqualizeVoltageSetPoint": 4151,
    "EqualizeTimeSetPoint":    4162,
    "EqualizeIntervalDay":     4163,
    "DaysBetweenBulkAbsorb":   4252,
    # AUX 1 control registers (Table 4165-3 thresholds & timings)
    "Aux1VoltsLoAbs":          4166,
    "Aux1DelayT":              4167,
    "Aux1HoldT":               4168,
    "Aux1VoltsHiAbs":          4172,
}

# Keys that must always be included in monitored parameters (forced in config_flow)
WRITABLE_PARAMETER_KEYS: list[str] = list(WRITABLE_REGISTERS.keys())

# ---------------------------------------------------------------------------
# EEPROM force-write constants (Force Flag Bits register 4160-4161)
# ForceEEpromUpdateWriteF = 0x00000004 — saves all (EE) registers to EEPROM
# Written as 32-bit value split across two 16-bit registers:
#   Low  word → register 4160 (Modbus address 4159) = 0x0004
#   High word → register 4161 (Modbus address 4160) = 0x0000
# ---------------------------------------------------------------------------
EEPROM_FORCE_WRITE_LOW_REG   = 4160   # register number — address = 4159
EEPROM_FORCE_WRITE_HIGH_REG  = 4161   # register number — address = 4160
EEPROM_FORCE_WRITE_LOW_VAL   = 0x0004
EEPROM_FORCE_WRITE_HIGH_VAL  = 0x0000

# MPPT mode register (ON/OFF control via bit 0)
MPPT_MODE_REGISTER = 4164   # register number — address = 4163

# Coordinator key in hass.data
COORDINATOR = "coordinator"

# ---------------------------------------------------------------------------
# AUX 1 Off - Auto - On  (select entity)
# Register 4165 (Aux12Function) bits 6,7 — Classic manual Table 4165-1:
#   Aux1OffAutoOn = (Aux12Function & 0xC0) >> 6
# Writing must be a read-modify-write: only bits 6-7 may change, every other
# bit of 4165 (Aux1Function, Aux2Function, Aux2OffAutoOn) must be preserved.
# ---------------------------------------------------------------------------
AUX12_FUNCTION_REGISTER = 4165   # register number — address = 4164
AUX1_OFF_AUTO_ON_MASK   = 0x00C0
AUX1_OFF_AUTO_ON_SHIFT  = 6

# Only the three operable values are offered. Value 3 ("Aux 1 Unimplemented")
# is documented as "Unassigned at present" and is therefore not selectable,
# but it is still rendered if the device happens to report it.
AUX1_OFF_AUTO_ON_OPTIONS: dict[int, str] = {
    0: "Aux 1 Off",    # Aux 1 output is forced OFF (0 Volts)
    1: "Aux 1 Auto",   # Aux 1 operates automatically as defined in Aux1Function
    2: "Aux 1 On",     # Aux 1 output is forced ON (~14 Volts)
}
AUX1_OFF_AUTO_ON_UNIMPLEMENTED = "Aux 1 Unimplemented"   # value 3, read-only

# ---------------------------------------------------------------------------
# Info Flag Bits — binary sensor metadata (Classic manual Table 4130-1)
# The decoder explodes register 4130/4131 into one boolean per documented flag.
# Format: key -> (friendly_name, device_class_str, icon, entity_category_str)
#
# device_class "problem" renders as Problem/OK, "heat" as Hot/Normal.
# entity_category "diagnostic" keeps the flag out of the main device controls.
# ---------------------------------------------------------------------------
INFO_FLAG_META: dict[str, tuple] = {
    "InfoFlag_Aux1StateOn":                ("Aux 1 State On",               None,      "mdi:electric-switch",       None),
    "InfoFlag_Aux2StateOn":                ("Aux 2 State On",               None,      "mdi:electric-switch",       None),
    "InfoFlag_EqualizeInProgress":         ("Equalize In Progress",         None,      "mdi:battery-sync",          None),
    "InfoFlag_EqDoneF":                    ("EqDoneF",                      None,      "mdi:battery-check",         "diagnostic"),
    "InfoFlag_EQMPPT":                     ("EQ MPPT",                      None,      "mdi:sun-wireless",          "diagnostic"),
    "InfoFlag_CurrentLimit":               ("Current Limit",                None,      "mdi:speedometer",           "diagnostic"),
    "InfoFlag_InVIsLowerThanOut":          ("In V is Lower Than Out",       None,      "mdi:arrow-down-thin",       "diagnostic"),
    "InfoFlag_BatteryTempSensorInstalled": ("Battery Temp Sensor Installed", None,     "mdi:thermometer-check",     "diagnostic"),
    "InfoFlag_PvPartialShadeF":            ("PvPartialShadeF",              None,      "mdi:weather-partly-cloudy", "diagnostic"),
    "InfoFlag_XtraInfo2DsplayF":           ("XtraInfo2DsplayF",             None,      "mdi:information-outline",   "diagnostic"),
    "InfoFlag_SerialWriteLock":            ("SerialWriteLock",              None,      "mdi:lock",                  "diagnostic"),
    "InfoFlag_UNLockJumperF":              ("UN-LockJumperF",               None,      "mdi:jump-rope",             "diagnostic"),
    "InfoFlag_XtraJumperF":                ("XtraJumperF",                  None,      "mdi:jump-rope",             "diagnostic"),
    "InfoFlag_StackumperF":                ("StackumperF",                  None,      "mdi:jump-rope",             "diagnostic"),
    "InfoFlag_WatchdogResetF":             ("WatchdogResetF",               None,      "mdi:restart-alert",         "diagnostic"),
    # --- Fault / problem flags ---
    "InfoFlag_ClassicOverTemperature":     ("Classic Over Temperature",     "heat",    "mdi:thermometer-alert",     "diagnostic"),
    "InfoFlag_EEPROMError":                ("EEPROM error",                 "problem", "mdi:memory",                "diagnostic"),
    "InfoFlag_HyperVoc":                   ("HyperVoc",                     "problem", "mdi:flash-alert",           "diagnostic"),
    "InfoFlag_GroundFaultF":               ("GroundFaultF",                 "problem", "mdi:flash-alert",           "diagnostic"),
    "InfoFlag_OCP":                        ("OCP (Over Current Protect)",   "problem", "mdi:fuse-alert",            "diagnostic"),
    "InfoFlag_ArcFaultF":                  ("ArcFaultF",                    "problem", "mdi:flash-alert",           "diagnostic"),
    "InfoFlag_NegBatCurrentF":             ("NegBatCurrentF",               "problem", "mdi:current-dc",            "diagnostic"),
    "InfoFlag_LowBatteryVF":               ("LowBatteryVF",                 "problem", "mdi:battery-alert",         "diagnostic"),
    "InfoFlag_TempCompShortedF":           ("TempCompShortedF",             "problem", "mdi:thermometer-alert",     "diagnostic"),
    "InfoFlag_InputShortedF":              ("InputShortedF",                "problem", "mdi:flash-off",             "diagnostic"),
}
