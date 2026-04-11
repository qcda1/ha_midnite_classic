"""DataUpdateCoordinator for Midnite Solar Classic."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .classic_reader import async_read_classic
from .classic_writer import WriteResult, write_register
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MidniteClassicCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls one Midnite Classic controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        scan_interval: int,
        device_name: str,
    ) -> None:
        self.host = host
        self.port = port
        self.device_name = device_name
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{host}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Classic controller."""
        data = await async_read_classic(self.host, self.port)
        if data is None:
            raise UpdateFailed(
                f"Failed to read data from Midnite Classic at {self.host}:{self.port}"
            )
        return data

    async def async_write_setpoint(
        self,
        param_key: str,
        ha_value: float,
    ) -> WriteResult:
        """Write a writable setpoint register and immediately refresh data.

        Called exclusively by ``MidniteClassicNumber.async_set_native_value()``.
        The coordinator refresh ensures HA entities reflect the confirmed
        device value rather than the optimistic one sent by the user.

        Parameters
        ----------
        param_key:  Key from ``WRITABLE_REGISTERS`` / ``PARAMETER_META``.
        ha_value:   New value in HA native units (volts, seconds, days…).

        Returns
        -------
        ``WriteResult`` — the number entity inspects ``.success`` / ``.error``
        to decide how to surface the outcome in HA.
        """
        result: WriteResult = await write_register(
            host=self.host,
            port=self.port,
            param_key=param_key,
            ha_value=ha_value,
        )

        if result.success:
            # Trigger an immediate poll so HA reflects the confirmed device value
            await self.async_request_refresh()
        else:
            _LOGGER.warning(
                "Setpoint write failed for %s — skipping refresh: %s",
                param_key,
                result.error,
            )

        return result