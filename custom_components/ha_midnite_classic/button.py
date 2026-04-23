"""Button platform for ha_midnite_classic — EEPROM persistence control.

Exposes a single ``ButtonEntity`` per Classic controller:

  "Save Settings to EEPROM"

Pressing this button triggers ``ForceEEpromUpdateWriteF`` (0x00000004) via
``classic_writer.force_eeprom_write()``, which writes all current (EE) register
values to the Classic's internal EEPROM so they survive a device reboot.

Typical workflow
----------------
1. Change one or more setpoint values using the number entities.
2. Press "Save Settings to EEPROM" to persist all changes permanently.

Without step 2, setpoint changes survive only until the next Classic reboot.
"""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .classic_writer import force_eeprom_write
from .const import CONF_HOST, CONF_PORT, COORDINATOR, DOMAIN
from .coordinator import MidniteClassicCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Save to EEPROM button for this Classic controller."""
    coordinator: MidniteClassicCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    data = entry.data
    host: str = data[CONF_HOST]
    port: int = int(data[CONF_PORT])
    device_name: str = (
        coordinator.data.get("Name", host) if coordinator.data else host
    )

    async_add_entities(
        [
            MidniteClassicEepromButton(
                host=host,
                port=port,
                device_name=device_name,
                entry_id=entry.entry_id,
            )
        ]
    )


class MidniteClassicEepromButton(ButtonEntity):
    """Button entity that forces an EEPROM save on the Classic controller.

    Pressing this button writes ``ForceEEpromUpdateWriteF`` to registers
    4160-4161, causing the Classic to persist all current (EE) register
    values to internal EEPROM.
    """

    _attr_has_entity_name = True
    _attr_name = "Save Settings to EEPROM"
    _attr_icon = "mdi:content-save-all"

    def __init__(
        self,
        host: str,
        port: int,
        device_name: str,
        entry_id: str,
    ) -> None:
        self._host = host
        self._port = port
        self._device_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_eeprom_save"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._host}:{self._port}")},
            name=self._device_name,
            manufacturer="Midnite Solar",
            model="Classic 150",
        )

    async def async_press(self) -> None:
        """Handle button press — trigger EEPROM force-write on the Classic.

        Flow
        ----
        1. Call ``force_eeprom_write()`` from classic_writer.
        2. On success: log info.
        3. On failure: log error + show a persistent notification in HA.
        """
        _LOGGER.debug(
            "EEPROM save button pressed for Classic at %s:%d", self._host, self._port
        )

        result = await force_eeprom_write(host=self._host, port=self._port)

        if result.success:
            _LOGGER.info(
                "EEPROM save successful for Classic at %s:%d", self._host, self._port
            )
            return

        # --- Write failed ---------------------------------------------------
        _LOGGER.error(
            "EEPROM save failed for Classic at %s:%d: %s",
            self._host,
            self._port,
            result.error,
        )

        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Midnite Classic — EEPROM Save Error",
                "message": (
                    f"Could not save settings to EEPROM on **{self._device_name}**.\n\n"
                    f"Your setpoint changes are active but will be lost on next reboot.\n\n"
                    f"Error: {result.error}"
                ),
                "notification_id": f"{DOMAIN}_eeprom_error_{self._host}",
            },
        )
