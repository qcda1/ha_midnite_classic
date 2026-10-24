"""Select platform for ha_midnite_classic — AUX 1 Off / Auto / On.

Exposes a single ``SelectEntity`` per Classic controller:

  "Aux 1 Mode"

The AUX 1 Off-Auto-On state lives in bits 6,7 of register 4165
(Aux12Function), per Classic manual Table 4165-1:

  0 → Aux 1 Off    — Aux 1 output is forced OFF (0 Volts)
  1 → Aux 1 Auto   — Aux 1 operates automatically as defined in Aux1Function
  2 → Aux 1 On     — Aux 1 output is forced ON (~14 Volts)
  3 → Aux 1 Unimplemented — unassigned at present (reported, never selectable)

The current state is read from the coordinator data dict (key
"Aux1OffAutoOn"), which the decoder already extracts, so no extra Modbus
reads are required.

Writing is delegated to ``classic_writer.write_aux1_off_auto_on()``, which
performs a read-modify-write so that the AUX 1 / AUX 2 function assignments
packed into the same register are preserved.

Note: register 4165 is marked (EE) in the Classic manual. Changes apply
immediately but survive a device reboot only if the user presses the
"Save Settings to EEPROM" button entity.
"""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .classic_writer import write_aux1_off_auto_on
from .const import (
    AUX1_OFF_AUTO_ON_OPTIONS,
    AUX1_OFF_AUTO_ON_UNIMPLEMENTED,
    CONF_HOST,
    CONF_PORT,
    COORDINATOR,
    DOMAIN,
)
from .coordinator import MidniteClassicCoordinator

_LOGGER = logging.getLogger(__name__)

# Coordinator data keys
_AUX1_STATE_KEY = "Aux1OffAutoOn"
_AUX12_RAW_KEY = "Aux12Function"

# Reverse map: option label → register value
_LABEL_TO_VALUE: dict[str, int] = {
    label: value for value, label in AUX1_OFF_AUTO_ON_OPTIONS.items()
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AUX 1 Off/Auto/On select for this Classic controller."""
    coordinator: MidniteClassicCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]

    data = entry.data
    host: str = data[CONF_HOST]
    port: int = int(data[CONF_PORT])
    device_name: str = coordinator.data.get("Name", host) if coordinator.data else host

    async_add_entities(
        [
            MidniteClassicAux1ModeSelect(
                coordinator=coordinator,
                host=host,
                port=port,
                device_name=device_name,
                entry_id=entry.entry_id,
            )
        ]
    )


class MidniteClassicAux1ModeSelect(
    CoordinatorEntity[MidniteClassicCoordinator], SelectEntity
):
    """Select entity controlling AUX 1 Off / Auto / On (register 4165, bits 6-7)."""

    _attr_has_entity_name = True
    _attr_name = "Aux 1 Mode"
    _attr_icon = "mdi:electric-switch"
    _attr_options = list(AUX1_OFF_AUTO_ON_OPTIONS.values())

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
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_aux1_off_auto_on"
        self.entity_id = f"select.{slugify(device_name)}_{slugify(self._attr_name)}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._host}:{self._port}")},
            name=self._device_name,
            manufacturer="Midnite Solar",
            model="Classic 150",
        )

    # ------------------------------------------------------------------
    # Current state — bits 6,7 of Aux12Function, already decoded
    # ------------------------------------------------------------------

    @property
    def current_option(self) -> str | None:
        """Return the current AUX 1 mode label, or None if unavailable."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(_AUX1_STATE_KEY)
        if raw is None:
            return None
        try:
            value = int(raw)
        except (TypeError, ValueError):
            return None

        if value in AUX1_OFF_AUTO_ON_OPTIONS:
            return AUX1_OFF_AUTO_ON_OPTIONS[value]

        # Value 3 is documented as "Unassigned at present". It is reported so
        # the user can see it, but it is not offered as a selectable option.
        if value == 3:
            _LOGGER.debug(
                "AUX 1 Off/Auto/On reports 3 (%s) on %s",
                AUX1_OFF_AUTO_ON_UNIMPLEMENTED,
                self._device_name,
            )
        else:
            _LOGGER.warning(
                "Unexpected Aux1OffAutoOn value %s on %s", value, self._device_name
            )
        return None

    def _current_aux12(self) -> int | None:
        """Return the current raw Aux12Function word, or None if unavailable."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(_AUX12_RAW_KEY)
        if raw is None:
            return None
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    async def async_select_option(self, option: str) -> None:
        """Write the selected AUX 1 mode to register 4165."""
        mode_value = _LABEL_TO_VALUE.get(option)
        if mode_value is None:
            _LOGGER.error("Unknown AUX 1 mode option requested: %s", option)
            return

        current_aux12 = self._current_aux12()
        if current_aux12 is None:
            # Writing on top of a value we could not read would wipe the AUX
            # function assignments packed into the same register.
            _LOGGER.error(
                "Aux12Function is unavailable for %s — AUX 1 mode write refused",
                self._device_name,
            )
            return

        result = await write_aux1_off_auto_on(
            host=self._host,
            port=self._port,
            mode_value=mode_value,
            current_aux12=current_aux12,
        )

        if result.success:
            await self.coordinator.async_request_refresh()
            return

        # --- Write failed ---------------------------------------------------
        _LOGGER.error(
            "Failed to set AUX 1 mode to %s for %s: %s",
            option,
            self._device_name,
            result.error,
        )

        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Midnite Classic — AUX 1 Mode Error",
                "message": (
                    f"Could not set AUX 1 to **{option}** on "
                    f"**{self._device_name}**.\n\nError: {result.error}"
                ),
                "notification_id": f"{DOMAIN}_aux1_mode_error_{self._host}",
            },
        )

        # Restore the displayed state from the last known device value
        self.async_write_ha_state()
