"""Switch platform for ha_midnite_classic — MPPT controller ON/OFF.

Exposes a single ``SwitchEntity`` per Classic controller:

  "MPPT Controller"

The ON/OFF state is encoded in the least significant bit (bit 0) of register
4164 (MpptMode), per Classic manual Table 4164-1:
  - Bit 0 = 1 → controller ON  (e.g. SOLAR ON  = 0x000B = 11)
  - Bit 0 = 0 → controller OFF (e.g. SOLAR OFF = 0x000A = 10)

Toggling the switch sets or clears bit 0 using bitwise OR / AND, preserving
the current MPPT mode value (SOLAR, WIND, HYDRO, etc.).

The current state is read from the coordinator data dict (key "MPPTMode"),
so no extra Modbus reads are required.

Note: register 4164 is marked (EE) in the Classic manual. Changes survive
only until the next device reboot unless the user presses the
"Save Settings to EEPROM" button entity.
"""

from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .classic_writer import write_mppt_onoff
from .const import CONF_HOST, CONF_PORT, COORDINATOR, DOMAIN
from .coordinator import MidniteClassicCoordinator

_LOGGER = logging.getLogger(__name__)

# Coordinator data key for the MPPT mode register value
_MPPT_MODE_KEY = "MPPTMode"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MPPT ON/OFF switch for this Classic controller."""
    coordinator: MidniteClassicCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    data = entry.data
    host: str = data[CONF_HOST]
    port: int = int(data[CONF_PORT])
    device_name: str = (
        coordinator.data.get("Name", host) if coordinator.data else host
    )

    async_add_entities(
        [
            MidniteClassicMpptSwitch(
                coordinator=coordinator,
                host=host,
                port=port,
                device_name=device_name,
                entry_id=entry.entry_id,
            )
        ]
    )


class MidniteClassicMpptSwitch(
    CoordinatorEntity[MidniteClassicCoordinator], SwitchEntity
):
    """Switch entity that controls the MPPT ON/OFF state of the Classic.

    State is derived from bit 0 of MPPTMode (register 4164).
    Writing sets or clears bit 0 while preserving the current mode value.
    """

    _attr_has_entity_name = True
    _attr_name = "MPPT Controller"
    _attr_icon = "mdi:solar-power-variant"

    def __init__(
        self,
        coordinator: MidniteClassicCoordinator,
        host: str,
        port: int,
        device_name: str,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._host = host
        self._port = port
        self._device_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_mppt_switch"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._host}:{self._port}")},
            name=self._device_name,
            manufacturer="Midnite Solar",
            model="Classic 150",
        )

    # ------------------------------------------------------------------
    # Current state — bit 0 of MPPTMode from coordinator data
    # ------------------------------------------------------------------

    @property
    def is_on(self) -> bool | None:
        """Return True if MPPT controller is ON (bit 0 of MPPTMode = 1)."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(_MPPT_MODE_KEY)
        if raw is None:
            return None
        try:
            return (int(raw) & 0x0001) == 1
        except (TypeError, ValueError):
            return None

    def _current_mode(self) -> int:
        """Return the current raw MPPTMode value, or 0 if unavailable."""
        if self.coordinator.data is None:
            return 0
        raw = self.coordinator.data.get(_MPPT_MODE_KEY)
        try:
            return int(raw) if raw is not None else 0
        except (TypeError, ValueError):
            return 0

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    async def _async_set_onoff(self, turn_on: bool) -> None:
        """Shared logic for turn_on / turn_off.

        Flow
        ----
        1. Write new MPPTMode value (bit 0 set or cleared).
        2. On success: trigger coordinator refresh.
        3. On failure: log error + persistent notification + restore state.
        """
        result = await write_mppt_onoff(
            host=self._host,
            port=self._port,
            turn_on=turn_on,
            current_mode=self._current_mode(),
        )

        if result.success:
            await self.coordinator.async_request_refresh()
            return

        # --- Write failed ---------------------------------------------------
        action = "ON" if turn_on else "OFF"
        _LOGGER.error(
            "Failed to set MPPT %s for %s: %s",
            action,
            self._device_name,
            result.error,
        )

        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": f"Midnite Classic — MPPT {action} Error",
                "message": (
                    f"Could not turn MPPT **{action}** on **{self._device_name}**.\n\n"
                    f"Error: {result.error}"
                ),
                "notification_id": f"{DOMAIN}_mppt_error_{self._host}",
            },
        )

        # Restore current state in UI
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:  # noqa: ANN003
        """Turn the MPPT controller ON (set bit 0 of MPPTMode)."""
        await self._async_set_onoff(turn_on=True)

    async def async_turn_off(self, **kwargs) -> None:  # noqa: ANN003
        """Turn the MPPT controller OFF (clear bit 0 of MPPTMode)."""
        await self._async_set_onoff(turn_on=False)
