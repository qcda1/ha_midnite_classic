"""Sensor platform for ha_midnite_classic."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_HOST,
    CONF_MONITORED_PARAMETERS,
    CONF_PORT,
    COORDINATOR,
    DEFAULT_PARAMETERS,
    DOMAIN,
    PARAMETER_META,
)
from .coordinator import MidniteClassicCoordinator

_LOGGER = logging.getLogger(__name__)

_DEVICE_CLASS_MAP: dict[str, SensorDeviceClass] = {
    "voltage":     SensorDeviceClass.VOLTAGE,
    "current":     SensorDeviceClass.CURRENT,
    "power":       SensorDeviceClass.POWER,
    "energy":      SensorDeviceClass.ENERGY,
    "temperature": SensorDeviceClass.TEMPERATURE,
}

_STATE_CLASS_MAP: dict[str, SensorStateClass] = {
    "measurement":      SensorStateClass.MEASUREMENT,
    "total":            SensorStateClass.TOTAL,
    "total_increasing": SensorStateClass.TOTAL_INCREASING,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Midnite Classic sensors."""
    coordinator: MidniteClassicCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    data = entry.data
    options = entry.options

    monitored: list[str] = options.get(
        CONF_MONITORED_PARAMETERS,
        data.get(CONF_MONITORED_PARAMETERS, DEFAULT_PARAMETERS),
    )

    host: str = data[CONF_HOST]
    port: int = int(data[CONF_PORT])
    device_name: str = (
        coordinator.data.get("Name", host) if coordinator.data else host
    )

    entities: list[MidniteClassicSensor] = []
    for param in monitored:
        if coordinator.data and param not in coordinator.data:
            _LOGGER.warning("Parameter %s not in Classic data — skipping", param)
            continue

        meta = PARAMETER_META.get(param)
        if meta:
            friendly_name, unit, dc_str, sc_str, icon, *rest = meta
            precision = rest[0] if rest else None
        else:
            friendly_name, unit, dc_str, sc_str, icon = param, None, None, None, None

        device_class  = _DEVICE_CLASS_MAP.get(dc_str)  if dc_str else None
        state_class   = _STATE_CLASS_MAP.get(sc_str)   if sc_str else None

        entities.append(
            MidniteClassicSensor(
                coordinator=coordinator,
                param_key=param,
                friendly_name=friendly_name,
                unit=unit,
                device_class=device_class,
                state_class=state_class,
                icon=icon,
                device_name=device_name,
                host=host,
                port=port,
                entry_id=entry.entry_id,
                precision=precision,
            )
        )

    async_add_entities(entities)


class MidniteClassicSensor(CoordinatorEntity[MidniteClassicCoordinator], SensorEntity):
    """One sensor entity per monitored Classic parameter."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MidniteClassicCoordinator,
        param_key: str,
        friendly_name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        icon: str | None,
        device_name: str,
        host: str,
        port: int,
        entry_id: str,
        precision: int | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._param_key = param_key
        self._attr_name = friendly_name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._device_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{param_key}"
        if precision:
            self._attr_suggested_display_precision = precision
        self._device_host = host
        self._device_port = port

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._device_host}:{self._device_port}")},
            name=self._device_name,
            manufacturer="Midnite Solar",
            model="Classic 150",
        )

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._param_key)
