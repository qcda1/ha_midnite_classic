"""Binary sensor platform for ha_midnite_classic — Info Flag Bits.

Register 4130/4131 (InfoFlagsBits) is a 32-bit status word. The decoder reads
it as a single value and additionally explodes it into one boolean per
documented flag (keys prefixed ``InfoFlag_``), following Classic manual
Table 4130-1. This platform turns each of those booleans into a binary sensor.

The raw ``InfoFlagsBits`` value is still available as a normal sensor, so
existing templates and automations built on top of it keep working unchanged.

All flags are read-only. Most are exposed as diagnostic entities; the ones
that describe normal operating state — AUX 1 / AUX 2 output state and
Equalize In Progress — are exposed as regular entities since they are what
automations typically act on (generator start/stop on the AUX 1 relay, for
instance).

Every flag carries the manufacturer's own description as an extra state
attribute, so the meaning of a flag is visible directly in the HA UI.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .classic_modbusdecoder import INFO_FLAG_BITS
from .const import CONF_HOST, CONF_PORT, COORDINATOR, DOMAIN, INFO_FLAG_META
from .coordinator import MidniteClassicCoordinator
from homeassistant.util import slugify

_LOGGER = logging.getLogger(__name__)

_DEVICE_CLASS_MAP: dict[str, BinarySensorDeviceClass] = {
    "problem": BinarySensorDeviceClass.PROBLEM,
    "heat": BinarySensorDeviceClass.HEAT,
    "running": BinarySensorDeviceClass.RUNNING,
}

_ENTITY_CATEGORY_MAP: dict[str, EntityCategory] = {
    "diagnostic": EntityCategory.DIAGNOSTIC,
}

# Index positions inside each INFO_FLAG_META tuple
_META_FRIENDLY = 0
_META_DEVICE_CLASS = 1
_META_ICON = 2
_META_CATEGORY = 3


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up one binary sensor per documented Info Flag Bit."""
    coordinator: MidniteClassicCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]

    data = entry.data
    host: str = data[CONF_HOST]
    port: int = int(data[CONF_PORT])
    device_name: str = coordinator.data.get("Name", host) if coordinator.data else host

    entities: list[MidniteClassicInfoFlag] = []
    for flag_key, meta in INFO_FLAG_META.items():
        bit_info = INFO_FLAG_BITS.get(flag_key)
        if bit_info is None:
            _LOGGER.warning(
                "Info flag %s has no entry in INFO_FLAG_BITS — skipping", flag_key
            )
            continue

        mask, manufacturer_name, description = bit_info

        entities.append(
            MidniteClassicInfoFlag(
                coordinator=coordinator,
                flag_key=flag_key,
                friendly_name=meta[_META_FRIENDLY],
                device_class=_DEVICE_CLASS_MAP.get(meta[_META_DEVICE_CLASS])
                if meta[_META_DEVICE_CLASS]
                else None,
                icon=meta[_META_ICON],
                entity_category=_ENTITY_CATEGORY_MAP.get(meta[_META_CATEGORY])
                if meta[_META_CATEGORY]
                else None,
                mask=mask,
                manufacturer_name=manufacturer_name,
                description=description,
                device_name=device_name,
                host=host,
                port=port,
                entry_id=entry.entry_id,
            )
        )

    async_add_entities(entities)


class MidniteClassicInfoFlag(
    CoordinatorEntity[MidniteClassicCoordinator], BinarySensorEntity
):
    """One binary sensor per bit of the InfoFlagsBits status word."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MidniteClassicCoordinator,
        flag_key: str,
        friendly_name: str,
        device_class: BinarySensorDeviceClass | None,
        icon: str | None,
        entity_category: EntityCategory | None,
        mask: int,
        manufacturer_name: str,
        description: str,
        device_name: str,
        host: str,
        port: int,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._flag_key = flag_key
        self._mask = mask
        self._manufacturer_name = manufacturer_name
        self._description = description
        self._device_name = device_name
        self._device_host = host
        self._device_port = port

        self._attr_name = friendly_name
        self._attr_device_class = device_class
        self._attr_icon = icon
        self._attr_entity_category = entity_category
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{flag_key}"
        self.entity_id = f"binary_sensor.{slugify(device_name)}_{slugify(friendly_name)}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._device_host}:{self._device_port}")},
            name=self._device_name,
            manufacturer="Midnite Solar",
            model="Classic 150",
        )

    @property
    def is_on(self) -> bool | None:
        """Return the decoded boolean for this flag."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self._flag_key)
        if value is None:
            return None
        return bool(value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the manufacturer's own naming and wording for this flag."""
        return {
            "flag_name": self._manufacturer_name,
            "description": self._description,
            "mask": f"0x{self._mask:08X}",
            "source_register": "4130/4131 (InfoFlagsBits)",
        }
