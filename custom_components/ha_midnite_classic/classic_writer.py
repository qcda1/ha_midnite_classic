"""Modbus write logic for writable Midnite Classic setpoint registers.

This module is intentionally separate from classic_reader.py and
classic_modbusdecoder.py to keep read (acquisition) and write (control)
responsibilities clearly isolated.

Write flow
----------
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
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import PARAMETER_META, WRITABLE_REGISTERS

_LOGGER = logging.getLogger(__name__)

# Index positions inside each PARAMETER_META tuple
_META_SCALE_IDX = 10   # scale factor (int | None)


@dataclass
class WriteResult:
    """Outcome of a single register write attempt.

    Attributes
    ----------
    success:    True if the Modbus write was acknowledged without error.
    param_key:  The PARAMETER_META key that was written.
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