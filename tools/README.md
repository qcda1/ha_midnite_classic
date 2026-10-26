# Midnite Solar Classic — Tool box

## 1- PrintRegisters.py

Utility program to read Midnite Solar Classic controller's registers and print them in different format. 

Require pymodbus Python module (pip install pymodbus)

```
python PrintRegisters.py --help
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



### Sample output:

```
$ python PrintRegisters.py -d 3
Sun Oct 25 17:00:41 2026
Host: 192.168.20.10
Connection =  True
List of Midnite Solar Classic registers (registres exclus omis).
Based on the register table in document: classic_register_map_Rev-C5-December-8-2013.pdf
List can be cut/paste in Excel for csv conversion using '-' as the separator value.



4101 - 1174   - R   - UNIT_ID                   - [4101]MSB = PCB revision, [4101]LSB = Unit Type
4102 - 2018   - R   - UNIT_SW_DATE_RO           - Year = [4102]
4103 - 518    - R   - UNIT_SW_DATE_RO           - Month = [4103]MSB, Day = [4103]LSB
4104 - 15     - R   - InfoFlagsBits3            - WhizBangJrCrcGood Bit 0x0001
4105 - 0      - —   - RESERVED                  - 
4106 - 12006  - R   - UNIT_MAC_AddressI         - [4108]MSB:[4108]LSB:[4107]MSB:[4107]LSB:[4106]MSB:[4106]LSB
4107 - 3840   - R   - UNIT_MAC_AddressI         - [4108]MSB:[4108]LSB:[4107]MSB:[4107]LSB:[4106]MSB:[4106]LSB
4108 - 24605  - R   - UNIT_MAC_AddressI         - [4108]MSB:[4108]LSB:[4107]MSB:[4107]LSB:[4106]MSB:[4106]LSB
4109 - 3999   - R   - WbJrAmpHourNET            - (([4110] << 16) + [4109]) Amp Hours
4110 - 0      - R   - WbJrAmpHourNET            - (([4110] << 16) + [4109]) Amp Hours
4111 - 13515  - R   - UNIT_Device_ID            - ([4112] << 16) + [4111]
4112 - 60387  - R   - UNIT_Device_ID            - ([4112] << 16) + [4111]
4113 - 24578  - R   - StatusRoll                - ([4113]>>12) Count + ([4113] & 0x0fff) Value
4114 - 1      - R   - RestartTimerms            - [4114] Milliseconds
4115 - 534    - R   - dispavgVbatt              - ([4115] /10) Volts
4116 - 535    - R   - dispavgVpv                - ([4116] /10) Volts
4117 - 4      - R   - IbattDisplayS             - ([4117] /10) Amps
4118 - 12     - R   - kW—Hours                  - ([4118] /10) kWatt—Hours
4119 - 21     - R   - Watts                     - [4119] Watts
4120 - 1540   - R   - ComboChargeStage          - Charge Stage = [4120]MSB, State = [4120]LSB
4121 - 3      - R   - PvInputCurrent            - ([4121] /10) Amps
4122 - 780    - R   - VocLastMeasured           - ([4122] /10) Volts
4123 - 1465   - R   - HighestVinputLog (EE)     - [4123] Voltage /10
4124 - 0      - R   - MatchPointShadow          - [4124]
...
```

## 2- TableauDeBord

This is a dashboard that show all pertinent data points, statuses and generator control parameters in
one single page. To minimize setup, make sure that the host name of your Classic is CLASSIC1 for a single
Classic setup and CLASSIC1 & CLASSIC2 on a two Classic installation. At the time of equipment creation in
Home Assistant, the equipment will be named after the host name and will fit the dashboard.


Refer to the dashboard's [README](TableauDeBord/README.md) file for installation instructions.

