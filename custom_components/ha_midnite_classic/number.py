"""Number platform for ha_midnite_classic — writable setpoint registers.

Each writable parameter defined in ``PARAMETER_META`` (writable=True) is
exposed as a ``NumberEntity`` in Home Assistant, allowing the user to change
setpoints directly from the HA UI or automations.

Read path  : values are sourced from the shared ``MidniteClassicCoordinator``
             (same data dict used by sensor.py) — no extra Modbus reads.
Write path : ``async_set_native_value()`` delegates to
             ``coordinator.async_write_setpoint()``, which calls
             ``classic_writer.write_register()`` and triggers a coordinator
             refresh on success.

Error handling (all three behaviours)
--------------------------------------
1. ``_LOGGER.error``          — always logged for traceability.
2. ``persistent_notification`` — visible banner in the HA UI.
3. ``async_write_ha_state()`` — entity value restored to last known good
                                value so the UI does not show a stale optimistic
                                value after a failed write.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_HOST,
    CONF_PORT,
    COORDINATOR,
    DOMAIN,
    PARAMETER_META,
    WRITABLE_PARAMETER_KEYS,
)
from .coordinator import MidniteClassicCoordinator

_LOGGER = logging.getLogger(__name__)

# Index positions inside each PARAMETER_META tuple
_META_FRIENDLY   = 0
_META_UNIT       = 1
_META_ICON       = 4
_META_PRECISION  = 5
_META_MIN        = 7
_META_MAX        = 8
_META_STEP       = 9


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Midnite Classic number entities for writable setpoints."""
    coordinator: MidniteClassicCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    data = entry.data
    host: str = data[CONF_HOST]
    port: int = int(data[CONF_PORT])
    device_name: str = (
        coordinator.data.get("Name", host) if coordinator.data else host
    )

    entities: list[MidniteClassicNumber] = []
    for param_key in WRITABLE_PARAMETER_KEYS:
        meta = PARAMETER_META.get(param_key)
        if meta is None:
            _LOGGER.warning("Writable param %s has no PARAMETER_META entry — skipping", param_key)
            continue

        entities.append(
            MidniteClassicNumber(
                coordinator=coordinator,
                param_key=param_key,
                friendly_name=meta[_META_FRIENDLY],
                unit=meta[_META_UNIT],
                icon=meta[_META_ICON],
                precision=meta[_META_PRECISION],
                min_value=meta[_META_MIN],
                max_value=meta[_META_MAX],
                step=meta[_META_STEP],
                device_name=device_name,
                host=host,
                port=port,
                entry_id=entry.entry_id,
            )
        )

    async_add_entities(entities)


class MidniteClassicNumber(CoordinatorEntity[MidniteClassicCoordinator], NumberEntity):
    """Editable number entity for one writable Classic setpoint register."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX   # shows a text-input box — precise entry

    def __init__(
        self,
        coordinator: MidniteClassicCoordinator,
        param_key: str,
        friendly_name: str,
        unit: str | None,
        icon: str | None,
        precision: int,
        min_value: float,
        max_value: float,
        step: float,
        device_name: str,
        host: str,
        port: int,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._param_key = param_key
        self._attr_name = friendly_name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        if precision:
            self._attr_suggested_display_precision = precision
        self._device_name = device_name
        self._device_host = host
        self._device_port = port
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{param_key}_number"

    # ------------------------------------------------------------------
    # Device grouping — same device as the sensor entities
    # ------------------------------------------------------------------

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._device_host}:{self._device_port}")},
            name=self._device_name,
            manufacturer="Midnite Solar",
            model="Classic 150",
        )

    # ------------------------------------------------------------------
    # Current value — sourced from the coordinator (read path)
    # ------------------------------------------------------------------

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self._param_key)
        if raw is None:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    async def async_set_native_value(self, value: float) -> None:
        """Handle a value change requested from the HA UI or an automation.

        Flow
        ----
        1. Delegate write + refresh to the coordinator.
        2. On failure: log, show a persistent notification, restore old value.
        """
        result = await self.coordinator.async_write_setpoint(
            param_key=self._param_key,
            ha_value=value,
        )

        if result.success:
            # Coordinator has already triggered async_request_refresh();
            # CoordinatorEntity will call async_write_ha_state() automatically
            # once fresh data arrives — nothing more to do here.
            return

        # --- Write failed: surface all three error behaviours ---------------

        # 1. Error log (always)
        _LOGGER.error(
            "Failed to write %s = %s: %s",
            self._param_key,
            value,
            result.error,
        )

        # 2. Persistent notification in HA UI
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Midnite Classic — Write Error",
                "message": (
                    f"Could not update **{self._attr_name}**.\n\n"
                    f"Value attempted: `{value}`\n"
                    f"Error: {result.error}"
                ),
                "notification_id": f"{DOMAIN}_write_error_{self._param_key}",
            },
        )

        # 3. Restore last known good value in the UI
        self.async_write_ha_state()
