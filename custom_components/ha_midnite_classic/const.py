"""Constants for the Midnite Solar Classic integration."""

DOMAIN = "ha_midnite_classic"
VERSION = "1.1.0"

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
    "Aux1Mode":                ("Aux 1 Mode",                None,  None,          None,                 "mdi:electric-switch",             0, False, None, None, None, None),
    "Aux2Mode":                ("Aux 2 Mode",                None,  None,          None,                 "mdi:electric-switch",             0, False, None, None, None, None),
    "VbatRegSetpoint":         ("Vbat Reg Setpoint",         "V",   "voltage",     None,                 "mdi:battery-lock",                0, False, None, None, None, None),
    "BatType":                 ("Battery Type",              None,  None,          None,                 "mdi:battery",                     0, False, None, None, None, None),
    "AbsorbVoltage":           ("Absorb Voltage",            "V",   "voltage",     None,                 "mdi:battery-arrow-up",            0, False, None, None, None, None),
    "FloatVoltage":            ("Float Voltage",             "V",   "voltage",     None,                 "mdi:battery-arrow-down",          0, False, None, None, None, None),
    "AbsorbEndAmps":           ("Absorb End Amps",           "A",   "current",     None,                 "mdi:current-dc",                  0, False, None, None, None, None),
    "ReasonForResting":        ("Reason For Resting",        None,  None,          None,                 "mdi:sleep",                       0, False, None, None, None, None),
    # --- Writable setpoints (number entities) ---
    # Modbus register numbers (not addresses): H4149–H4151, H4162, H4163, H4252
    # Address sent to device = register - 1 (per Modbus spec / Classic manual)
    "AbsorbVoltageSetPoint":   ("Absorb Voltage Setpoint",   "V",   "voltage",     "measurement",        "mdi:solar-panel",                 1, True,  10.0, 65.0, 0.1, 10),
    "FloatVoltageSetPoint":    ("Float Voltage Setpoint",    "V",   "voltage",     "measurement",        "mdi:solar-panel",                 1, True,  10.0, 65.0, 0.1, 10),
    "EqualizeVoltageSetPoint": ("Equalize Voltage Setpoint", "V",   "voltage",     "measurement",        "mdi:solar-panel",                 1, True,  10.0, 65.0, 0.1, 10),
    "EqualizeTimeSetPoint":    ("Equalize Time Setpoint",    "s",   None,          None,                 "mdi:timer",                       0, True,  0,    480,  1,   1),
    "EqualizeIntervalDay":     ("Equalize Interval Day",     "day", None,          None,                 "mdi:numeric",                     0, True,  0,    255,  1,   1),
    "DaysBetweenBulkAbsorb":   ("Days Between Bulk/Absorb",  "day", None,          None,                 "mdi:numeric",                     0, True,  0,    255,  1,   1),
}

# Modbus register numbers for writable setpoints (address = register - 1)
# Per Classic manual note: packet sends address = register - 1
WRITABLE_REGISTERS: dict[str, int] = {
    "AbsorbVoltageSetPoint":   4149,
    "FloatVoltageSetPoint":    4150,
    "EqualizeVoltageSetPoint": 4151,
    "EqualizeTimeSetPoint":    4162,
    "EqualizeIntervalDay":     4163,
    "DaysBetweenBulkAbsorb":  4252,
}

# Keys that must always be included in monitored parameters (forced in config_flow)
WRITABLE_PARAMETER_KEYS: list[str] = list(WRITABLE_REGISTERS.keys())

# Coordinator key in hass.data
COORDINATOR = "coordinator"