"""Modbus write logic for writable Midnite Classic setpoint registers.

This module is intentionally separate from classic_reader.py and
classic_modbusdecoder.py to keep read (acquisition) and write (control)
responsibilities clearly isolated.

Write flow — setpoint registers
---------------------------------
1. Caller provides the parameter key and the new value in HA units.
2. ``write_register()`` looks up the Modbus register number and scale factor
   from ``WRITABLE_REGISTERS`` and ``PARAMETER_META``.
3. The HA value is multiplied by ``scale`` and rounded to an integer to
   produce the raw Modbus word.
4. The raw word is written to address = register - 1, as required by the
   Modbus specification and documented in the Classic manual:
       "The modbus specification adds one (1) to the address sent to the unit
        to access a register, so that registers start at 1 rather than 0."
5. A ``WriteResult`` dataclass is returned so the caller can decide how to
   surface success or failure to the user without any HA-specific imports
   in this module.

Write flow — MPPT ON/OFF control
----------------------------------
Register 4164 (MpptMode) encodes both the MPPT mode and the ON/OFF state
in its least significant bit (Classic manual Table 4164-1):
  - Bit 0 = 1 → MPPT ON  (e.g. SOLAR = 0x000B = 11)
  - Bit 0 = 0 → MPPT OFF (e.g. SOLAR = 0x000A = 10)

``write_mppt_onoff()`` reads the current MPPTMode value from the coordinator
data dict, sets or clears bit 0, and writes the result back to register 4164.
Using bitwise OR/AND is more robust than ±1 as it is idempotent.

Write flow — AUX 1 Off / Auto / On control
-------------------------------------------
Register 4165 (Aux12Function) packs four independent fields into one word
(Classic manual Tables 4165-1 to 4165-4):

    bits 0-5   Aux1Function
    bits 6,7   Aux1OffAutoOn      <-- the only field this writer changes
    bits 8-13  Aux2Function
    bits 14,15 Aux2OffAutoOn

``write_aux1_off_auto_on()`` therefore performs a read-modify-write: it takes
the current Aux12Function value from the coordinator data, clears bits 6-7,
inserts the requested mode, and writes the whole word back. Writing the mode
value on its own would silently wipe the AUX 1 and AUX 2 function assignments.

Write flow — EEPROM persistence
---------------------------------
The Classic stores writable setpoints in RAM only. Values are lost on device
reboot unless explicitly saved to internal EEPROM.

``force_eeprom_write()`` triggers this save by writing the 32-bit flag value
``ForceEEpromUpdateWriteF = 0x00000004`` to the Force Flag Bits register pair
4160-4161 (Classic manual Table 4160-1):
  - Low  word (0x0004) → register 4160, address 4159
  - High word (0x0000) → register 4161, address 4160

This should be called by the user via the dedicated "Save to EEPROM" button
entity after completing all desired setpoint changes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import (
    AUX1_OFF_AUTO_ON_MASK,
    AUX1_OFF_AUTO_ON_SHIFT,
    AUX12_FUNCTION_REGISTER,
    EEPROM_FORCE_WRITE_HIGH_REG,
    EEPROM_FORCE_WRITE_HIGH_VAL,
    EEPROM_FORCE_WRITE_LOW_REG,
    EEPROM_FORCE_WRITE_LOW_VAL,
    MPPT_MODE_REGISTER,
    PARAMETER_META,
    WRITABLE_REGISTERS,
)

_LOGGER = logging.getLogger(__name__)

# Index positions inside each PARAMETER_META tuple
_META_SCALE_IDX = 10   # scale factor (int | None)


@dataclass
class WriteResult:
    """Outcome of a single register write attempt.

    Attributes
    ----------
    success:    True if the Modbus write was acknowledged without error.
    param_key:  The PARAMETER_META key that was written (or 'eeprom' /
                'mppt_onoff' for special writes).
    raw_value:  The integer word actually sent to the device.
    error:      Human-readable error message when success is False.
    """

    success: bool
    param_key: str
    raw_value: int
    error: str | None = None


async def write_register(
    host: str,
    port: int,
    param_key: str,
    ha_value: float,
) -> WriteResult:
    """Write a single setpoint register to the Classic controller.

    Parameters
    ----------
    host:       IP address of the Classic on the local network.
    port:       Modbus TCP port (normally 502).
    param_key:  Key from ``WRITABLE_REGISTERS`` / ``PARAMETER_META``.
    ha_value:   New value expressed in HA native units (e.g. volts, seconds,
                days).  Will be multiplied by the ``scale`` from
                ``PARAMETER_META`` before transmission.

    Returns
    -------
    ``WriteResult`` — the caller inspects ``.success`` and ``.error``.
    """

    # --- Validate that the key is writable -----------------------------------
    if param_key not in WRITABLE_REGISTERS:
        msg = f"{param_key} is not in WRITABLE_REGISTERS — write refused"
        _LOGGER.error(msg)
        return WriteResult(success=False, param_key=param_key, raw_value=0, error=msg)

    register_number: int = WRITABLE_REGISTERS[param_key]

    # Modbus address = register number - 1  (Classic manual / Modbus spec)
    modbus_address: int = register_number - 1

    # --- Determine scale factor from PARAMETER_META --------------------------
    meta = PARAMETER_META.get(param_key)
    if meta is None:
        msg = f"{param_key} not found in PARAMETER_META — write refused"
        _LOGGER.error(msg)
        return WriteResult(success=False, param_key=param_key, raw_value=0, error=msg)

    scale: int = meta[_META_SCALE_IDX] if meta[_META_SCALE_IDX] is not None else 1

    # --- Encode HA value → raw Modbus integer --------------------------------
    raw_value: int = round(ha_value * scale)

    _LOGGER.debug(
        "Writing %s: HA value=%.4f → raw=%d  (register %d, address %d, scale ×%d)",
        param_key,
        ha_value,
        raw_value,
        register_number,
        modbus_address,
        scale,
    )

    # --- Perform the Modbus TCP write ----------------------------------------
    client = AsyncModbusTcpClient(host=host, port=port)
    try:
        await client.connect()
        if not client.connected:
            msg = f"Could not connect to Classic at {host}:{port}"
            _LOGGER.error(msg)
            return WriteResult(
                success=False, param_key=param_key, raw_value=raw_value, error=msg
            )

        response = await client.write_register(
            address=modbus_address,
            value=raw_value,
        )

        if response.isError():
            msg = (
                f"Modbus error writing {param_key} "
                f"(register {register_number}, raw {raw_value}): {response}"
            )
            _LOGGER.error(msg)
            return WriteResult(
                success=False, param_key=param_key, raw_value=raw_value, error=msg
            )

        _LOGGER.info(
            "Successfully wrote %s = %.4f (raw %d) to register %d",
            param_key,
            ha_value,
            raw_value,
            register_number,
        )
        return WriteResult(success=True, param_key=param_key, raw_value=raw_value)

    except ModbusException as exc:
        msg = f"ModbusException writing {param_key}: {exc}"
        _LOGGER.error(msg)
        return WriteResult(
            success=False, param_key=param_key, raw_value=raw_value, error=msg
        )
    except Exception as exc:  # noqa: BLE001
        msg = f"Unexpected error writing {param_key}: {exc}"
        _LOGGER.error(msg)
        return WriteResult(
            success=False, param_key=param_key, raw_value=raw_value, error=msg
        )
    finally:
        client.close()


async def write_mppt_onoff(
    host: str,
    port: int,
    turn_on: bool,
    current_mode: int,
) -> WriteResult:
    """Set or clear the ON/OFF bit (bit 0) of the MPPTMode register (4164).

    The Classic encodes the MPPT mode and its ON/OFF state in register 4164:
      - Bit 0 = 1 → controller ON  (e.g. SOLAR ON  = 0x000B = 11)
      - Bit 0 = 0 → controller OFF (e.g. SOLAR OFF = 0x000A = 10)

    Bitwise OR/AND is used rather than ±1 to make the operation idempotent —
    calling turn_on when already ON, or turn_off when already OFF, is safe.

    Parameters
    ----------
    host:           IP address of the Classic.
    port:           Modbus TCP port (normally 502).
    turn_on:        True to set bit 0 (ON), False to clear it (OFF).
    current_mode:   Current raw value of MPPTMode from the coordinator data.

    Returns
    -------
    ``WriteResult`` with param_key='mppt_onoff'.
    """

    if turn_on:
        new_value: int = current_mode | 0x0001   # set bit 0
    else:
        new_value = current_mode & 0xFFFE         # clear bit 0

    modbus_address: int = MPPT_MODE_REGISTER - 1  # 4163

    _LOGGER.debug(
        "MPPT %s: current_mode=%d (0x%04X) → new_value=%d (0x%04X), address=%d",
        "ON" if turn_on else "OFF",
        current_mode, current_mode,
        new_value, new_value,
        modbus_address,
    )

    client = AsyncModbusTcpClient(host=host, port=port)
    try:
        await client.connect()
        if not client.connected:
            msg = f"Could not connect to Classic at {host}:{port} for MPPT ON/OFF"
            _LOGGER.error(msg)
            return WriteResult(
                success=False,
                param_key="mppt_onoff",
                raw_value=new_value,
                error=msg,
            )

        response = await client.write_register(
            address=modbus_address,
            value=new_value,
        )

        if response.isError():
            msg = (
                f"Modbus error writing MPPT {'ON' if turn_on else 'OFF'} "
                f"(register {MPPT_MODE_REGISTER}, raw {new_value}): {response}"
            )
            _LOGGER.error(msg)
            return WriteResult(
                success=False,
                param_key="mppt_onoff",
                raw_value=new_value,
                error=msg,
            )

        _LOGGER.info(
            "MPPT set to %s successfully (register %d, raw %d)",
            "ON" if turn_on else "OFF",
            MPPT_MODE_REGISTER,
            new_value,
        )
        return WriteResult(success=True, param_key="mppt_onoff", raw_value=new_value)

    except ModbusException as exc:
        msg = f"ModbusException writing MPPT ON/OFF: {exc}"
        _LOGGER.error(msg)
        return WriteResult(
            success=False,
            param_key="mppt_onoff",
            raw_value=new_value,
            error=msg,
        )
    except Exception as exc:  # noqa: BLE001
        msg = f"Unexpected error writing MPPT ON/OFF: {exc}"
        _LOGGER.error(msg)
        return WriteResult(
            success=False,
            param_key="mppt_onoff",
            raw_value=new_value,
            error=msg,
        )
    finally:
        client.close()


async def force_eeprom_write(host: str, port: int) -> WriteResult:
    """Save all current (EE) register values to the Classic's internal EEPROM.

    Triggers ``ForceEEpromUpdateWriteF`` (0x00000004) by writing the 32-bit
    Force Flag Bits register pair 4160-4161 (Classic manual Table 4160-1).

    The 32-bit value is split into two 16-bit Modbus writes:
      - Low  word: 0x0004 → register 4160, Modbus address 4159
      - High word: 0x0000 → register 4161, Modbus address 4160

    Both writes are performed within a single Modbus TCP connection.

    Returns
    -------
    ``WriteResult`` with param_key='eeprom'.
    """

    low_address:  int = EEPROM_FORCE_WRITE_LOW_REG  - 1   # 4159
    high_address: int = EEPROM_FORCE_WRITE_HIGH_REG - 1   # 4160

    _LOGGER.debug(
        "Forcing EEPROM write: low word 0x%04X → address %d, "
        "high word 0x%04X → address %d",
        EEPROM_FORCE_WRITE_LOW_VAL,  low_address,
        EEPROM_FORCE_WRITE_HIGH_VAL, high_address,
    )

    client = AsyncModbusTcpClient(host=host, port=port)
    try:
        await client.connect()
        if not client.connected:
            msg = f"Could not connect to Classic at {host}:{port} for EEPROM write"
            _LOGGER.error(msg)
            return WriteResult(
                success=False,
                param_key="eeprom",
                raw_value=EEPROM_FORCE_WRITE_LOW_VAL,
                error=msg,
            )

        # Write low word first (contains the flag bit)
        resp_low = await client.write_register(
            address=low_address,
            value=EEPROM_FORCE_WRITE_LOW_VAL,
        )
        if resp_low.isError():
            msg = f"Modbus error writing EEPROM force flag (low word): {resp_low}"
            _LOGGER.error(msg)
            return WriteResult(
                success=False,
                param_key="eeprom",
                raw_value=EEPROM_FORCE_WRITE_LOW_VAL,
                error=msg,
            )

        # Write high word (0x0000 — clears upper 16 bits of Force Flag)
        resp_high = await client.write_register(
            address=high_address,
            value=EEPROM_FORCE_WRITE_HIGH_VAL,
        )
        if resp_high.isError():
            msg = f"Modbus error writing EEPROM force flag (high word): {resp_high}"
            _LOGGER.error(msg)
            return WriteResult(
                success=False,
                param_key="eeprom",
                raw_value=EEPROM_FORCE_WRITE_HIGH_VAL,
                error=msg,
            )

        _LOGGER.info(
            "EEPROM force-write successful for Classic at %s:%d", host, port
        )
        return WriteResult(
            success=True,
            param_key="eeprom",
            raw_value=EEPROM_FORCE_WRITE_LOW_VAL,
        )

    except ModbusException as exc:
        msg = f"ModbusException during EEPROM force-write: {exc}"
        _LOGGER.error(msg)
        return WriteResult(
            success=False,
            param_key="eeprom",
            raw_value=EEPROM_FORCE_WRITE_LOW_VAL,
            error=msg,
        )
    except Exception as exc:  # noqa: BLE001
        msg = f"Unexpected error during EEPROM force-write: {exc}"
        _LOGGER.error(msg)
        return WriteResult(
            success=False,
            param_key="eeprom",
            raw_value=EEPROM_FORCE_WRITE_LOW_VAL,
            error=msg,
        )
    finally:
        client.close()


async def write_aux1_off_auto_on(
    host: str,
    port: int,
    mode_value: int,
    current_aux12: int,
) -> WriteResult:
    """Set the AUX 1 Off/Auto/On field (bits 6,7) of register 4165.

    This is a read-modify-write against ``current_aux12``: every other field
    packed into Aux12Function (Aux1Function, Aux2Function, Aux2OffAutoOn) is
    preserved untouched.

    Parameters
    ----------
    host:           IP address of the Classic.
    port:           Modbus TCP port (normally 502).
    mode_value:     0 = Aux 1 Off, 1 = Aux 1 Auto, 2 = Aux 1 On
                    (Classic manual Table 4165-1).
    current_aux12:  Current raw Aux12Function value from the coordinator data.

    Returns
    -------
    ``WriteResult`` with param_key='aux1_off_auto_on'.

    Note
    ----
    Register 4165 is marked (EE). The new value applies immediately but is lost
    on device reboot unless the user presses "Save Settings to EEPROM".
    """

    if mode_value not in (0, 1, 2):
        msg = f"Invalid AUX 1 Off/Auto/On value {mode_value} — write refused"
        _LOGGER.error(msg)
        return WriteResult(
            success=False, param_key="aux1_off_auto_on", raw_value=0, error=msg
        )

    new_value: int = (current_aux12 & ~AUX1_OFF_AUTO_ON_MASK) | (
        mode_value << AUX1_OFF_AUTO_ON_SHIFT
    )
    new_value &= 0xFFFF

    modbus_address: int = AUX12_FUNCTION_REGISTER - 1  # 4164

    _LOGGER.debug(
        "AUX 1 Off/Auto/On: mode=%d, current Aux12Function=%d (0x%04X) "
        "→ new=%d (0x%04X), address=%d",
        mode_value,
        current_aux12, current_aux12,
        new_value, new_value,
        modbus_address,
    )

    client = AsyncModbusTcpClient(host=host, port=port)
    try:
        await client.connect()
        if not client.connected:
            msg = f"Could not connect to Classic at {host}:{port} for AUX 1 mode"
            _LOGGER.error(msg)
            return WriteResult(
                success=False,
                param_key="aux1_off_auto_on",
                raw_value=new_value,
                error=msg,
            )

        response = await client.write_register(
            address=modbus_address,
            value=new_value,
        )

        if response.isError():
            msg = (
                f"Modbus error writing AUX 1 mode {mode_value} "
                f"(register {AUX12_FUNCTION_REGISTER}, raw {new_value}): {response}"
            )
            _LOGGER.error(msg)
            return WriteResult(
                success=False,
                param_key="aux1_off_auto_on",
                raw_value=new_value,
                error=msg,
            )

        _LOGGER.info(
            "AUX 1 Off/Auto/On set to %d successfully (register %d, raw %d)",
            mode_value,
            AUX12_FUNCTION_REGISTER,
            new_value,
        )
        return WriteResult(
            success=True, param_key="aux1_off_auto_on", raw_value=new_value
        )

    except ModbusException as exc:
        msg = f"ModbusException writing AUX 1 mode: {exc}"
        _LOGGER.error(msg)
        return WriteResult(
            success=False,
            param_key="aux1_off_auto_on",
            raw_value=new_value,
            error=msg,
        )
    except Exception as exc:  # noqa: BLE001
        msg = f"Unexpected error writing AUX 1 mode: {exc}"
        _LOGGER.error(msg)
        return WriteResult(
            success=False,
            param_key="aux1_off_auto_on",
            raw_value=new_value,
            error=msg,
        )
    finally:
        client.close()
