"""Constants for the Midnite Solar Classic integration."""

DOMAIN = "ha_midnite_classic"
VERSION = "1.0.0"

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
# Format: key -> (friendly_name, unit, device_class_str, state_class_str, icon)
PARAMETER_META: dict[str, tuple] = {
    "PCB":                    ("PCB Version",              None,  None,          None,                 "mdi:chip"),
    "Type":                   ("Controller Type",          None,  None,          None,                 "mdi:solar-power"),
    "Year":                   ("Firmware Year",            None,  None,          None,                 "mdi:calendar"),
    "Month":                  ("Firmware Month",           None,  None,          None,                 "mdi:calendar"),
    "Day":                    ("Firmware Day",             None,  None,          None,                 "mdi:calendar"),
    "InfoFlagBits3":          ("Info Flag Bits 3",         None,  None,          None,                 "mdi:flag"),
    "mac_0":                  ("MAC Byte 0",               None,  None,          None,                 "mdi:ethernet"),
    "mac_1":                  ("MAC Byte 1",               None,  None,          None,                 "mdi:ethernet"),
    "mac_2":                  ("MAC Byte 2",               None,  None,          None,                 "mdi:ethernet"),
    "mac_3":                  ("MAC Byte 3",               None,  None,          None,                 "mdi:ethernet"),
    "mac_4":                  ("MAC Byte 4",               None,  None,          None,                 "mdi:ethernet"),
    "mac_5":                  ("MAC Byte 5",               None,  None,          None,                 "mdi:ethernet"),
    "unitID":                 ("Unit ID",                  None,  None,          None,                 "mdi:identifier"),
    "StatusRoll":             ("Status Roll",              None,  None,          None,                 "mdi:information"),
    "RsetTmms":               ("Reset Time ms",            "ms",  None,          None,                 "mdi:timer"),
    "BatVoltage":             ("Battery Voltage",          "V",   "voltage",     "measurement",        "mdi:battery"),
    "PVVoltage":              ("PV Voltage",               "V",   "voltage",     "measurement",        "mdi:solar-panel"),
    "BatCurrent":             ("Battery Current",          "A",   "current",     "measurement",        "mdi:current-dc"),
    "EnergyToday":            ("Energy Today",             "kWh", "energy",      "total_increasing",   "mdi:calendar-today"),
    "Power":                  ("Power",                    "W",   "power",       "measurement",        "mdi:flash"),
    "ChargeStage":            ("Charge Stage",             None,  None,          None,                 "mdi:battery-charging"),
    "State":                  ("State",                    None,  None,          None,                 "mdi:state-machine"),
    "PVCurrent":              ("PV Current",               "A",   "current",     "measurement",        "mdi:current-dc"),
    "lastVOC":                ("Last VOC",                 "V",   "voltage",     "measurement",        "mdi:solar-panel"),
    "HighestVinputLog":       ("Highest Vin Log",          None,  None,          None,                 "mdi:chart-line"),
    "MatchPointShadow":       ("Match Point Shadow",       None,  None,          None,                 "mdi:weather-cloudy"),
    "AmpHours":               ("Amp Hours",                "Ah",  None,          "total_increasing",   "mdi:battery-charging"),
    "TotalEnergy":            ("Total Energy",             "kWh", "energy",      "total_increasing",   "mdi:lightning-bolt"),
    "LifetimeAmpHours":       ("Lifetime Amp Hours",       "Ah",  None,          "total_increasing",   "mdi:battery-high"),
    "InfoFlagsBits":          ("Info Flags Bits",          None,  None,          None,                 "mdi:flag-variant"),
    "BatTemperature":         ("Battery Temperature",      "°C",  "temperature", "measurement",        "mdi:thermometer"),
    "FETTemperature":         ("FET Temperature",          "°C",  "temperature", "measurement",        "mdi:thermometer"),
    "PCBTemperature":         ("PCB Temperature",          "°C",  "temperature", "measurement",        "mdi:thermometer"),
    "NiteMinutesNoPwr":       ("Night Minutes No Power",   "min", None,          "measurement",        "mdi:weather-night"),
    "MinuteLogIntervalSec":   ("Log Interval",             "s",   None,          None,                 "mdi:timer"),
    "modbus_port_register":   ("Modbus Port",              None,  None,          None,                 "mdi:lan"),
    "FloatTimeTodaySeconds":  ("Float Time Today",         "s",   None,          "measurement",        "mdi:timer"),
    "AbsorbTime":             ("Absorb Time",              "s",   None,          None,                 "mdi:timer"),
    "PWM_ReadOnly":           ("PWM",                      None,  None,          "measurement",        "mdi:pulse"),
    "Reason_For_Reset":       ("Reason For Reset",         None,  None,          None,                 "mdi:restart"),
    "EqualizeTime":           ("Equalize Time",            "s",   None,          None,                 "mdi:timer"),
    "WbangJrCmdS":            ("WhizBang Jr Command",      None,  None,          None,                 "mdi:remote"),
    "WizBangJrRawCurrent":    ("WhizBang Jr Raw Current",  "A",   "current",     "measurement",        "mdi:current-dc"),
    "Name":                   ("Device Name",              None,  None,          None,                 "mdi:tag"),
    "ChargeStateText":        ("Charge State Text",        None,  None,          None,                 "mdi:battery-charging-outline"),
    "MPPTMode":               ("MPPT Mode",                None,  None,          None,                 "mdi:sun-wireless"),
    "Aux1Mode":               ("Aux 1 Mode",               None,  None,          None,                 "mdi:electric-switch"),
    "Aux2Mode":               ("Aux 2 Mode",               None,  None,          None,                 "mdi:electric-switch"),
    "VbatRegSetpoint":        ("Vbat Reg Setpoint",        "V",   "voltage",     None,                 "mdi:battery-lock"),
    "BatType":                ("Battery Type",             None,  None,          None,                 "mdi:battery"),
    "AbsorbVoltage":          ("Absorb Voltage",           "V",   "voltage",     None,                 "mdi:battery-arrow-up"),
    "FloatVoltage":           ("Float Voltage",            "V",   "voltage",     None,                 "mdi:battery-arrow-down"),
    "AbsorbEndAmps":          ("Absorb End Amps",          "A",   "current",     None,                 "mdi:current-dc"),
    "ReasonForResting":       ("Reason For Resting",       None,  None,          None,                 "mdi:sleep"),
    "AbsorbVoltageSetPoint":  ("Absorb Voltage setpoint",  "V",   "voltage",     "measurement",        "mdi:solar-panel"),
    "FloatVoltageSetPoint":   ("Float Voltage setpoint",   "V",   "voltage",     "measurement",        "mdi:solar-panel"),
    "EqualizeVoltageSetPoint":  ("Equalize Voltage setpoint",  "V",   "voltage", "measurement",        "mdi:solar-panel"),
    "EqualizeTimeSetPoint":   ("Equalize Time Setpoint",   "s",   None,          None,                 "mdi:timer"),
    "EqualizeIntervalDay":    ("Equalize Interval Day",    "day", None,          None,                 "mdi:numeric"),
    "DaysBetweenBulkAbsorb":  ("DaysBetweenBulkAbsorb",    "day", None,          None,                 "mdi:numeric"),

}

# Coordinator key in hass.data
COORDINATOR = "coordinator"
