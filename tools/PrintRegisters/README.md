# PrintRegister.py

Small program to extract and print the content of a Midnite Solar Classic solar charge controller.

> Note: It is important to understand that the register definitions are based on Midnite Solat register map document provided in this repository and dated back to 2013. For example, this program allowed me to discover that registers 4166 and 4172 contain the SOC% lower and upper limit setpoints of AUX1 function SOC% High and Low. See the list below for these two registers. This feature arrived after the document and was never updated. I will update this program once I'm done finding all the Aux1 related registers (still looking for the Aux1 state value register).

You need pymodbus module to run this program

`pip install pymodbus`

The programm works fine with pymodbus version 3.12.1

## Sample usage

python PrintRegisters.py --help

```text

usage: PrintRegisters.py [-h] [-i IP] [-d DETAIL] [-x | -b | -a] [-r XXXX-YYYY] [-e EXCLUDE] [-l LOGLVL] [-s]

Fetch and print Midnite Solar Classic registers, excluding registers listed in an exclusion file. Useful for narrowing
down which register holds an undocumented value.

options:
  -h, --help            show this help message and exit
  -i, --ip IP           IP address of the Midnite Classic (default: 192.168.20.10)
  -d, --detail DETAIL   Level of detail (0 to 4) (default: 2)
  -x, --hexa            Print values in hexadecimal 16 bits (default: False)
  -b, --bin             Print values in binary 16 bits, zero padded (default: False)
  -a, --all             Print values in decimal, hexadecimal and binary (default: False)
  -r, --range XXXX-YYYY
                        Range of registers to print, e.g. 4115-4130. Use the same value twice for a single register,
                        e.g. 4115-4115 (default: (4101, 4384))
  -e, --exclude EXCLUDE
                        Text file listing registers to exclude (one per line, or ranges 'NNNN-MMMM'). Ignored silently
                        if the file doesn't exist. (default: exclude.txt)
  -l, --loglvl LOGLVL   Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
  -s, --silence         Mode silencieux: seules les lignes de registres sont imprimées sur stdout (aucun bandeau, aucun
                        message de log). Les logs vont sur stderr. Utile avec crontab + redirection vers un fichier
                        (default: False)

Output uses '-' as separator for easy csv import in Excel.

```

## Output example

python PrintRegisters.py -a

```text

Fri Jul  3 21:08:30 2026
Host: 192.168.20.10
Connection =  True
List of Midnite Solar Classic registers.
Based on the register table in document: classic_register_map_Rev-C5-December-8-2013.pdf
List can be cut/paste in Excel for csv conversion using '-' as the separator value.
Printing registers in decimal - hexadecimal - binary...



4101 - 1174   - 0496 - 0000010010010110 - R   - UNIT_ID
4102 - 2018   - 07e2 - 0000011111100010 - R   - UNIT_SW_DATE_RO
4103 - 518    - 0206 - 0000001000000110 - R   - UNIT_SW_DATE_RO
4104 - 15     - 000f - 0000000000001111 - R   - InfoFlagsBits3
4105 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4106 - 12006  - 2ee6 - 0010111011100110 - R   - UNIT_MAC_AddressI
4107 - 3840   - 0f00 - 0000111100000000 - R   - UNIT_MAC_AddressI
4108 - 24605  - 601d - 0110000000011101 - R   - UNIT_MAC_AddressI
4109 - 3851   - 0f0b - 0000111100001011 - R   - WbJrAmpHourNET
4110 - 0      - 0000 - 0000000000000000 - R   - WbJrAmpHourNET
4111 - 13515  - 34cb - 0011010011001011 - R   - UNIT_Device_ID
4112 - 60387  - ebe3 - 1110101111100011 - R   - UNIT_Device_ID
4113 - 5561   - 15b9 - 0001010110111001 - R   - StatusRoll
4114 - 1      - 0001 - 0000000000000001 - R   - RestartTimerms
4115 - 532    - 0214 - 0000001000010100 - R   - dispavgVbatt
4116 - 228    - 00e4 - 0000000011100100 - R   - dispavgVpv
4117 - 0      - 0000 - 0000000000000000 - R   - IbattDisplayS
4118 - 23     - 0017 - 0000000000010111 - R   - kW—Hours
4119 - 0      - 0000 - 0000000000000000 - R   - Watts
4120 - 0      - 0000 - 0000000000000000 - R   - ComboChargeStage
4121 - 0      - 0000 - 0000000000000000 - R   - PvInputCurrent
4122 - 228    - 00e4 - 0000000011100100 - R   - VocLastMeasured
4123 - 1465   - 05b9 - 0000010110111001 - R   - HighestVinputLog (EE)
4124 - 0      - 0000 - 0000000000000000 - R   - MatchPointShadow
4125 - 44     - 002c - 0000000000101100 - R   - AmpHours
4126 - 20892  - 519c - 0101000110011100 - R   - Lifetime kW—Hours (EE)
4127 - 1      - 0001 - 0000000000000001 - R   - Lifetime kW—Hours (EE)
4128 - 34847  - 881f - 1000100000011111 - R   - LifetimeAmpHours (EE)
4129 - 2      - 0002 - 0000000000000010 - R   - LifetimeAmpHours (EE)
4130 - 4356   - 1104 - 0001000100000100 - R   - InfoFlagsBits
4131 - 45568  - b200 - 1011001000000000 - R   - InfoFlagsBits2
4132 - 241    - 00f1 - 0000000011110001 - R   - BATTtemperature
4133 - 354    - 0162 - 0000000101100010 - R   - FETtemperature
4134 - 433    - 01b1 - 0000000110110001 - R   - PCBTemperature
4135 - 21     - 0015 - 0000000000010101 - R   - NiteMinutesNoPwr
4136 - 300    - 012c - 0000000100101100 - R/W - MinuteLogIntervalSec (EE)
4137 - 502    - 01f6 - 0000000111110110 - R/W - modbus_port_register (EE)
4138 - 7403   - 1ceb - 0001110011101011 - R   - FloatTimeTodaySeconds
4139 - 3600   - 0e10 - 0000111000010000 - R/W - AbsorbTime
4140 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4141 - 1325   - 052d - 0000010100101101 - R   - PWM_ReadOnly
4142 - 4      - 0004 - 0000000000000100 - R   - Reason_For_Reset
4143 - 279    - 0117 - 0000000100010111 - R/W - Equalize Time
4144 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4145 - 1      - 0001 - 0000000000000001 - R/W - MppWLast
4146 - 0      - 0000 - 0000000000000000 - R/W - USBcommMODE (EE)
4147 - 0      - 0000 - 0000000000000000 - R/W - NoDoubleClickTimer
4148 - 880    - 0370 - 0000001101110000 - R/W - Battery output Current Limit (EE)
4149 - 560    - 0230 - 0000001000110000 - R/W - Absorb Set Point Voltage (EE)
4150 - 552    - 0228 - 0000001000101000 - R/W - Float Voltage Set Point (EE)
4151 - 560    - 0230 - 0000001000110000 - R/W - Equalize Voltage Set Point (EE)
4152 - 880    - 0370 - 0000001101110000 - R   - Sliding Current Limit
4153 - 0      - 0000 - 0000000000000000 - R/W - Minimum Absorb Time (EE)
4154 - 3600   - 0e10 - 0000111000010000 - R/W - Absorb Time (EE)
4155 - 660    - 0294 - 0000001010010100 - R/W - Maximum Battery Temperature Compensation Voltage (EE)
4156 - 504    - 01f8 - 0000000111111000 - R/W - Minimum Battery Temperature Compensation Voltage (EE)
4157 - 0      - 0000 - 0000000000000000 - R/W - Battery Temp Comp Value for each 2V cell (EE)
4158 - 0      - 0000 - 0000000000000000 - R/W - General Purpose 16 bit word (EE)
4159 - 0      - 0000 - 0000000000000000 - R/W - EqualizeReTryDays (EE)
4160 - 0      - 0000 - 0000000000000000 - W   - Force Flag Bits
4161 - 0      - 0000 - 0000000000000000 - W   - Force Flag Bits
4162 - 279    - 0117 - 0000000100010111 - R/W - Equalize Time (EE)
4163 - 0      - 0000 - 0000000000000000 - R/W - Equalize Interval Days (EE)
4164 - 11     - 000b - 0000000000001011 - R/W - Mppt Mode / Solar, Wind, etc. (EE)
4165 - 4695   - 1257 - 0001001001010111 - R/W - Aux 1 and 2 Function (EE)
4166 - 93     - 005d - 0000000001011101 - R/W - Aux1VoltsLoAbs (EE)
4167 - 10     - 000a - 0000000000001010 - R/W - Aux1DelayT (EE)
4168 - 10     - 000a - 0000000000001010 - R/W - Aux1HoldT (EE)
4169 - 2      - 0002 - 0000000000000010 - R/W - Aux2PwmVwidth (EE)
4170 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4171 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4172 - 95     - 005f - 0000000001011111 - R/W - Aux1VoltsHiAbs (EE)
4173 - 372    - 0174 - 0000000101110100 - R/W - Aux2VoltsHiAbs (EE)
4174 - 250    - 00fa - 0000000011111010 - R/W - Aux1VoltsLoRel (EE)
4175 - 1024   - 0400 - 0000010000000000 - R/W - Aux1VoltsHiRel (EE)
4176 - 65530  - fffa - 1111111111111010 - R/W - Aux2VoltsLoRel (EE)
4177 - 0      - 0000 - 0000000000000000 - R/W - Aux2VoltsHiRel (EE)
4178 - 91     - 005b - 0000000001011011 - R/W - Aux1VoltsLoPv (EE)
4179 - 95     - 005f - 0000000001011111 - R/W - Aux1VoltsHiPv (EE)
4180 - 357    - 0165 - 0000000101100101 - R/W - VariMax (EE)
4181 - 95     - 005f - 0000000001011111 - R/W - Aux2VoltsHiPv (EE)
4182 - 0      - 0000 - 0000000000000000 - R/W - EnableFlags3 (EE)
4183 - 202    - 00ca - 0000000011001010 - R/W - ArcFaultSenstvty (EE)
4184 - 85     - 0055 - 0000000001010101 - —   - RESERVED
4185 - 256    - 0100 - 0000000100000000 - —   - RESERVED
4186 - 18636  - 48cc - 0100100011001100 - R/W - EnableFlags2 (EE)
4187 - 65     - 0041 - 0000000001000001 - R/W - EnableFlagsBits (EE)
4188 - 0      - 0000 - 0000000000000000 - R/W - RESERVED FACTORY CALIBRATION
4189 - 65535  - ffff - 1111111111111111 - R/W - Vbatt_Offset (EE)
4190 - 0      - 0000 - 0000000000000000 - R/W - Vpv_Offset (EE)
4191 - 228    - 00e4 - 0000000011100100 - R   - VpvTargetRd
4192 - 200    - 00c8 - 0000000011001000 - R/W - VpvTargetWr (EE)
4193 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4194 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4195 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4196 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4197 - 5      - 0005 - 0000000000000101 - R/W - SweepIntervalSecs (EE)
4198 - 100    - 0064 - 0000000001100100 - R/W - MinSwpVoltage (EE)
4199 - 990    - 03de - 0000001111011110 - R/W - MaxInputCurrent (EE)
4200 - 10     - 000a - 0000000000001010 - R/W - SweepDepth (EE)
4201 - 8      - 0008 - 0000000000001000 - R/W - NegativeCurrent Adj. (EE)
4202 - 732    - 02dc - 0000001011011100 - R   - ClipperCmdVolts
4203 - 0      - 0000 - 0000000000000000 - R/W - WindNumberOfPoles (EE)
4204 - 10     - 000a - 0000000000001010 - R/W - MppPercentVoc (EE)
4205 - 0      - 0000 - 0000000000000000 - R/W - WindTableToUse (EE)
4206 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4207 - 3      - 0003 - 0000000000000011 - R/W - LEDmode (EE)
4208 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4209 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4210 - 19523  - 4c43 - 0100110001000011 - R/W - ID name (EE)
4211 - 21313  - 5341 - 0101001101000001 - R/W - ID name (EE)
4212 - 18771  - 4953 - 0100100101010011 - R/W - ID name (EE)
4213 - 12611  - 3143 - 0011000101000011 - R/W - ID name (EE)
4214 - 2318   - 090e - 0000100100001110 - R   - CTIME0
4215 - 789    - 0315 - 0000001100010101 - R   - CTIME0
4216 - 1795   - 0703 - 0000011100000011 - R   - CTIME1
4217 - 2026   - 07ea - 0000011111101010 - R   - CTIME1
4218 - 96     - 0060 - 0000000001100000 - R   - CTIME2
4219 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4220 - 0      - 0000 - 0000000000000000 - R/W - RemoteMenuMode
4221 - 0      - 0000 - 0000000000000000 - W   - RemoteButtons
4222 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4223 - 65522  - fff2 - 1111111111110010 - —   - RESERVED
4224 - 228    - 00e4 - 0000000011100100 - R/W - PreVoc (do not write)
4225 - 6      - 0006 - 0000000000000110 - —   - RESERVED
4226 - 0      - 0000 - 0000000000000000 - R/W - Aux2_A2D_D2A
4227 - 1      - 0001 - 0000000000000001 - —   - RESERVED
4228 - 1      - 0001 - 0000000000000001 - —   - RESERVED
4229 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4230 - 228    - 00e4 - 0000000011100100 - —   - RESERVED
4231 - 228    - 00e4 - 0000000011100100 - R   - VocRD
4232 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4233 - 229    - 00e5 - 0000000011100101 - —   - RESERVED
4234 - 528    - 0210 - 0000001000010000 - —   - RESERVED
4235 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4236 - 3600   - 0e10 - 0000111000010000 - R/W - AbsorbTime (duplicate)
4237 - 50     - 0032 - 0000000000110010 - R/W - AntiClickSenstvty (EE)
4238 - 10565  - 2945 - 0010100101000101 - R/W - SiestaTime
4239 - 20     - 0014 - 0000000000010100 - R   - SiestaAbortVocAdj
4240 - 8192   - 2000 - 0010000000000000 - R   - flagsRD
4241 - 512    - 0200 - 0000001000000000 - R   - flagsRD
4242 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4243 - 300    - 012c - 0000000100101100 - —   - RESERVED
4244 - 552    - 0228 - 0000001000101000 - R   - VbattRegSetPTmpComp
4245 - 48     - 0030 - 0000000000110000 - R/W - VbattNominal (EE)
4246 - 20     - 0014 - 0000000000010100 - R/W - EndingAmps (EE)
4247 - 10     - 000a - 0000000000001010 - R/W - EndingSoc (EE)
4248 - 500    - 01f4 - 0000000111110100 - —   - EndAmpSocMBaddress
4249 - 510    - 01fe - 0000000111111110 - R/W - RebulkVolts (EE)
4250 - 99     - 0063 - 0000000001100011 - R   - BattMonVolts
4251 - 42     - 002a - 0000000000101010 - R   - BattMonSOC
4252 - 3      - 0003 - 0000000000000011 - R   - DaysBtwnBulkAbs (EE)
4253 - 41     - 0029 - 0000000000101001 - R   - BattMonAHefficiency (EE)
4254 - 0      - 0000 - 0000000000000000 - R/W - DayLogCombCatIndex
4255 - 0      - 0000 - 0000000000000000 - R   - LogValueRead
4256 - 0      - 0000 - 0000000000000000 - R/W - MinLogCombCatIndex
4257 - 0      - 0000 - 0000000000000000 - R/W - RebulkTimerSec
4258 - 1465   - 05b9 - 0000010110111001 - —   - RESERVED
4259 - 3      - 0003 - 0000000000000011 - —   - RESERVED
4260 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4261 - 4      - 0004 - 0000000000000100 - —   - RESERVED
4262 - 1694   - 069e - 0000011010011110 - —   - RESERVED
4263 - 40     - 0028 - 0000000000101000 - —   - RESERVED
4264 - 1      - 0001 - 0000000000000001 - R/W - Voc_Qualify_Timer_1ms
4265 - 0      - 0000 - 0000000000000000 - R/W - Voc_Qualify_Timer_1ms
4266 - 0      - 0000 - 0000000000000000 - R   - IpvMinus
4267 - 42     - 002a - 0000000000101010 - —   - RESERVED
4268 - 41     - 0029 - 0000000000101001 - —   - RESERVED
4269 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4270 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4271 - 1      - 0001 - 0000000000000001 - R   - RestartTimerms
4272 - 42     - 002a - 0000000000101010 - R   - Ibatt
4273 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4274 - 238    - 00ee - 0000000011101110 - —   - RESERVED
4275 - 5      - 0005 - 0000000000000101 - R   - ReasonForResting
4276 - 534    - 0216 - 0000001000010110 - R   - Output Vbatt
4277 - 228    - 00e4 - 0000000011100100 - R   - Input Vpv
4278 - 150    - 0096 - 0000000010010110 - —   - RESERVED
4279 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4280 - 235    - 00eb - 0000000011101011 - —   - RESERVED
4281 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4282 - 0      - 0000 - 0000000000000000 - R   - PkHoldVpvStamp
4283 - 228    - 00e4 - 0000000011100100 - R   - VpvTargetRd (temporary)
4284 - 0      - 0000 - 0000000000000000 - R   - SwpDeepTimeoutSec
4285 - 606    - 025e - 0000001001011110 - —   - RESERVED
4286 - 20     - 0014 - 0000000000010100 - R/W - LowWatts (EE)
4287 - 50     - 0032 - 0000000000110010 - R/W - WindLowWatts (dflt=50) (EE)
4288 - 25     - 0019 - 0000000000011001 - R/W - WindWindowWattsRef (EE)
4289 - 57536  - e0c0 - 1110000011000000 - R   - WindowWattsRO
4290 - 90     - 005a - 0000000001011010 - R/W - WindTimeOutRef (EE)
4291 - 1800   - 0708 - 0000011100001000 - R/W - WindTimeOut2Ref (EE)
4292 - 0      - 0000 - 0000000000000000 - R/W - WindTimeOut
4293 - 2747   - 0abb - 0000101010111011 - R/W - WindTimeOut2
4294 - 693    - 02b5 - 0000001010110101 - R   - MinVpvTurnOn
4295 - 0      - 0000 - 0000000000000000 - R   - VpvB4TurnOff
4296 - 65472  - ffc0 - 1111111111000000 - R/W - HydroSwpAmps10Time6
4297 - 0      - 0000 - 0000000000000000 - R/W - EndingAmpsTimerSec
4298 - 1295   - 050f - 0000010100001111 - R/W - PkAmpsOverLimitHi (EE)
4299 - 980    - 03d4 - 0000001111010100 - R/W - PkAmpsOverLimitLo (EE)
4300 - 0      - 0000 - 0000000000000000 - R/W - FactoryVbattOffset (EE)
4301 - 23386  - 5b5a - 0101101101011010 - R/W - WindPowerTableV +0 (EE)
4302 - 24156  - 5e5c - 0101111001011100 - R/W - WindPowerTableV +1 (EE)
4303 - 25184  - 6260 - 0110001001100000 - R/W - WindPowerTableV +2 (EE)
4304 - 26212  - 6664 - 0110011001100100 - R/W - WindPowerTableV +3 (EE)
4305 - 27240  - 6a68 - 0110101001101000 - R/W - WindPowerTableV +4 (EE)
4306 - 28268  - 6e6c - 0110111001101100 - R/W - WindPowerTableV +5 (EE)
4307 - 29296  - 7270 - 0111001001110000 - R/W - WindPowerTableV +6 (EE)
4308 - 30836  - 7874 - 0111100001110100 - R/W - WindPowerTableV +7 (EE)
4309 - 256    - 0100 - 0000000100000000 - R/W - WindPowerTableI +0 (EE)
4310 - 770    - 0302 - 0000001100000010 - R/W - WindPowerTableI +1 (EE)
4311 - 1284   - 0504 - 0000010100000100 - R/W - WindPowerTableI +2 (EE)
4312 - 1798   - 0706 - 0000011100000110 - R/W - WindPowerTableI +3 (EE)
4313 - 2312   - 0908 - 0000100100001000 - R/W - WindPowerTableI +4 (EE)
4314 - 2826   - 0b0a - 0000101100001010 - R/W - WindPowerTableI +5 (EE)
4315 - 3340   - 0d0c - 0000110100001100 - R/W - WindPowerTableI +6 (EE)
4316 - 3854   - 0f0e - 0000111100001110 - R/W - WindPowerTableI +7 (EE)
4317 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4318 - 1297   - 0511 - 0000010100010001 - R/W - PkAmpsOverTrip (EE)
4319 - 0      - 0000 - 0000000000000000 - R   - mngp_revision
4320 - 0      - 0000 - 0000000000000000 - R   - mnlp_revision
4321 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4322 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4323 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4324 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4325 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4326 - 10     - 000a - 0000000000001010 - R/W - ClassicModbusAddr (EE)
4327 - 21002  - 520a - 0101001000001010 - R/W - BatteryTempPassed
4328 - 524    - 020c - 0000001000001100 - R   - iFlagsRO Low
4329 - 0      - 0000 - 0000000000000000 - R   - iFlagsRO High
4330 - 0      - 0000 - 0000000000000000 - R/W - ModbusControl
4331 - 0      - 0000 - 0000000000000000 - R/W - ClassicFmePassedBits
4332 - 0      - 0000 - 0000000000000000 - R/W - WindSynchA
4333 - 0      - 0000 - 0000000000000000 - R/W - WindSynchV
4334 - 15     - 000f - 0000000000001111 - R/W - FollowMePassRef (EE)
4335 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4336 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4337 - 100    - 0064 - 0000000001100100 - —   - RESERVED
4338 - 709    - 02c5 - 0000001011000101 - —   - RESERVED
4339 - 46229  - b495 - 1011010010010101 - —   - RESERVED
4340 - 64     - 0040 - 0000000001000000 - —   - RESERVED
4341 - 17572  - 44a4 - 0100010010100100 - R   - DabtU32Debug01
4342 - 1096   - 0448 - 0000010001001000 - R   - DabtU32Debug02
4343 - 34420  - 8674 - 1000011001110100 - R   - DabtU32Debug03
4344 - 27903  - 6cff - 0110110011111111 - R   - DabtU32Debug04
4345 - 38983  - 9847 - 1001100001000111 - —   - RESERVED
4346 - 51946  - caea - 1100101011101010 - —   - RESERVED
4347 - 46433  - b561 - 1011010101100001 - —   - RESERVED
4348 - 30736  - 7810 - 0111100000010000 - —   - RESERVED
4349 - 10565  - 2945 - 0010100101000101 - —   - RESERVED
4350 - 1      - 0001 - 0000000000000001 - —   - RESERVED
4351 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4352 - 8419   - 20e3 - 0010000011100011 - R   - CRC Network
4353 - 51207  - c807 - 1100100000000111 - R   - CRC Application
4354 - 0      - 0000 - 0000000000000000 - R/W - ClearLogsCat
4355 - 0      - 0000 - 0000000000000000 - R   - ClearLogsCounter10ms
4356 - 54     - 0036 - 0000000000110110 - R/W - User Variable 02
4357 - 53     - 0035 - 0000000000110101 - R   - WizBangRxBufferTempSh1
4358 - 20030  - 4e3e - 0100111000111110 - R   - WizBangRxBufferTempSh2
4359 - 37     - 0025 - 0000000000100101 - R   - WizBangRxBufferTempSh3
4360 - 37     - 0025 - 0000000000100101 - R   - WizBangRxBufferTempSh4
4361 - 53     - 0035 - 0000000000110101 - R/W - WbangJrCmdS (EE)
4362 - 62     - 003e - 0000000000111110 - R   - WizBangJrRawCurrent
4363 - 0      - 0000 - 0000000000000000 - R/W - WbJrNumeratorSS (EE)
4364 - 64     - 0040 - 0000000001000000 - —   - RESERVED
4365 - 55994  - daba - 1101101010111010 - R   - WbJrAmpHourPOSitive
4366 - 0      - 0000 - 0000000000000000 - R   - WbJrAmpHourPOSitive
4367 - 13393  - 3451 - 0011010001010001 - R   - WbJrAmpHourNEGative
4368 - 65535  - ffff - 1111111111111111 - R   - WbJrAmpHourNEGative
4369 - 3851   - 0f0b - 0000111100001011 - R   - WbJrAmpHourNET
4370 - 0      - 0000 - 0000000000000000 - R   - WbJrAmpHourNET
4371 - 65487  - ffcf - 1111111111001111 - R   - WzBangJrCurrent32Signed
4372 - 9550   - 254e - 0010010101001110 - R   - WizBangJrRawCrcAndtemp
4373 - 96     - 0060 - 0000000001100000 - —   - RESERVED
4374 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4375 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4376 - 16     - 0010 - 0000000000010000 - —   - RESERVED
4377 - 484    - 01e4 - 0000000111100100 - —   - RESERVED
4378 - 64780  - fd0c - 1111110100001100 - —   - RESERVED
4379 - 250    - 00fa - 0000000011111010 - —   - RESERVED
4380 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4381 - 500    - 01f4 - 0000000111110100 - —   - RESERVED
4382 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4383 - 0      - 0000 - 0000000000000000 - —   - RESERVED
4384 - 0      - 0000 - 0000000000000000 - —   - RESERVED
2026-07-03 21:08:30 - INFO - Lecture terminée sans erreur.


```
