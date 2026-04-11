"""
Wrapper around classic_modbusdecoder.py 
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Sentinel errors so config_flow can show a specific message
class ClassicModuleNotFoundError(Exception):
    """Raised when classic_modbusdecoder.py is missing from the integration folder."""

class ClassicConnectionError(Exception):
    """Raised when the Modbus TCP connection to the device fails."""


async def async_read_classic(host: str, port: int) -> dict[str, Any] | None:
    """Read all registers from a Midnite Classic controller (non-blocking).

    Returns:
        dict  — data from the device
        None  — connection/read error (logged)

    Raises:
        ClassicModuleNotFoundError — if classic_modbusdecoder.py is missing
    """
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(None, _read_classic_sync, host, port)
    except ClassicModuleNotFoundError:
        raise  # re-raise so config_flow can show a specific error
    except Exception as exc:  # noqa: BLE001
        _LOGGER.error("Error reading Classic at %s:%s — %s", host, port, exc)
        return None


def _read_classic_sync(host: str, port: int) -> dict[str, Any]:
    """Synchronous Modbus read — executed in a thread pool."""
    try:
        from .classic_modbusdecoder import getRegisters  # type: ignore[import]
    except ImportError as exc:
        raise ClassicModuleNotFoundError(
            "classic_modbusdecoder.py not found in the integration folder. "
            "Download it from https://github.com/qcda1/MidniteClassic and place it in "
            "custom_components/ha_midnite_classic/"
        ) from exc

    data = getRegisters(ip=host, port=port)

    if not data:
        raise ClassicConnectionError(
            f"getRegisters returned empty data for {host}:{port}"
        )

    return data
