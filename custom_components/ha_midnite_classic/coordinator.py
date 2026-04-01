"""DataUpdateCoordinator for Midnite Solar Classic."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .classic_reader import async_read_classic
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
