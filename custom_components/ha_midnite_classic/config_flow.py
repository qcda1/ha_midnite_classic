"""Config flow for Midnite Solar Classic (ha_midnite_classic)."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.config_entries import OptionsFlow

from .classic_reader import ClassicModuleNotFoundError, async_read_classic
from .const import (
    CONF_HOST,
    CONF_MONITORED_PARAMETERS,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PARAMETERS,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    PARAMETER_META,
    WRITABLE_PARAMETER_KEYS,
)

_LOGGER = logging.getLogger(__name__)


def _ensure_writable_keys(selected: list[str]) -> list[str]:
    """Guarantee that all writable setpoint keys are always included.

    Writable parameters must always be present as monitored parameters so
    that the coordinator data dict contains their current values, which are
    displayed by the corresponding NumberEntity.  The user cannot opt out of
    these keys via the UI (the checkboxes are pre-checked and locked).
    """
    for key in WRITABLE_PARAMETER_KEYS:
        if key not in selected:
            selected.append(key)
    return selected


def _connection_schema(host: str = "", port: int = DEFAULT_PORT,
                       scan_interval: int = DEFAULT_SCAN_INTERVAL) -> vol.Schema:
    """Build the step-1 schema (reused in options flow)."""
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=host): selector.selector({"text": {}}),
            vol.Required(CONF_PORT, default=port): selector.selector(
                {"number": {"min": 1, "max": 65535, "mode": "box"}}
            ),
            vol.Required(CONF_SCAN_INTERVAL, default=scan_interval): selector.selector(
                {
                    "number": {
                        "min": MIN_SCAN_INTERVAL,
                        "max": MAX_SCAN_INTERVAL,
                        "unit_of_measurement": "s",
                        "mode": "slider",
                    }
                }
            ),
        }
    )


class MidniteClassicConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ha_midnite_classic."""

    VERSION = 1

    def __init__(self) -> None:
        self._host: str = ""
        self._port: int = DEFAULT_PORT
        self._scan_interval: int = DEFAULT_SCAN_INTERVAL
        self._device_name: str = "Classic"
        self._available_params: list[str] = []

    # ------------------------------------------------------------------
    # Step 1 — connection + scan interval
    # ------------------------------------------------------------------
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input[CONF_PORT])
            scan_interval = int(user_input[CONF_SCAN_INTERVAL])

            try:
                data = await async_read_classic(host, port)
            except ClassicModuleNotFoundError:
                errors["base"] = "module_not_found"
                data = None

            if data is None and "base" not in errors:
                errors["base"] = "cannot_connect"

            if not errors:
                self._host = host
                self._port = port
                self._scan_interval = scan_interval
                self._device_name = str(data.get("Name", host))

                self._available_params = [k for k in PARAMETER_META if k in data]
                for k in data:
                    if k not in self._available_params:
                        self._available_params.append(k)

                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()

                return await self.async_step_parameters()

        return self.async_show_form(
            step_id="user",
            data_schema=_connection_schema(self._host, self._port, self._scan_interval),
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Step 2 — select monitored parameters
    # ------------------------------------------------------------------
    async def async_step_parameters(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            selected = [p for p in self._available_params if user_input.get(p, False)]
            # Always include writable setpoint keys regardless of user selection
            selected = _ensure_writable_keys(selected)
            return self.async_create_entry(
                title=self._device_name,
                data={
                    CONF_HOST: self._host,
                    CONF_PORT: self._port,
                    CONF_SCAN_INTERVAL: self._scan_interval,
                    CONF_MONITORED_PARAMETERS: selected,
                },
            )

        fields: dict[vol.Marker, Any] = {}
        for param in self._available_params:
            # Writable params are pre-checked; user can still uncheck them in
            # the UI but _ensure_writable_keys() will re-add them on submit.
            default = param in DEFAULT_PARAMETERS or param in WRITABLE_PARAMETER_KEYS
            fields[vol.Optional(param, default=default)] = selector.selector({"boolean": {}})

        return self.async_show_form(
            step_id="parameters",
            data_schema=vol.Schema(fields),
            description_placeholders={"device_name": self._device_name},
        )

    # ------------------------------------------------------------------
    # Options flow
    # ------------------------------------------------------------------
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlow:
        return MidniteClassicOptionsFlowHandler()


class MidniteClassicOptionsFlowHandler(OptionsFlow):
    """Options flow — adjust interval and monitored parameters."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        data = dict(self.config_entry.data)
        options = dict(self.config_entry.options)

        host: str = data[CONF_HOST]
        port: int = int(data[CONF_PORT])
        current_interval: int = int(options.get(
            CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        ))
        current_params: list[str] = options.get(
            CONF_MONITORED_PARAMETERS,
            data.get(CONF_MONITORED_PARAMETERS, DEFAULT_PARAMETERS),
        )

        if user_input is not None:
            new_interval = int(user_input.pop(CONF_SCAN_INTERVAL))
            selected = [k for k, v in user_input.items() if v]
            # Always include writable setpoint keys regardless of user selection
            selected = _ensure_writable_keys(selected)
            return self.async_create_entry(
                title="",
                data={CONF_SCAN_INTERVAL: new_interval, CONF_MONITORED_PARAMETERS: selected},
            )

        try:
            live_data = await async_read_classic(host, port)
        except ClassicModuleNotFoundError:
            errors["base"] = "module_not_found"
            live_data = None

        if live_data:
            available_params = [k for k in PARAMETER_META if k in live_data]
            for k in live_data:
                if k not in available_params:
                    available_params.append(k)
        else:
            if "base" not in errors:
                errors["base"] = "cannot_connect"
            available_params = list(PARAMETER_META.keys())

        fields: dict[vol.Marker, Any] = {
            vol.Required(CONF_SCAN_INTERVAL, default=current_interval): selector.selector(
                {
                    "number": {
                        "min": MIN_SCAN_INTERVAL,
                        "max": MAX_SCAN_INTERVAL,
                        "unit_of_measurement": "s",
                        "mode": "slider",
                    }
                }
            ),
        }
        for param in available_params:
            # Writable params are pre-checked; _ensure_writable_keys() enforces
            # them on submit even if the user unchecks them.
            default = param in current_params or param in WRITABLE_PARAMETER_KEYS
            fields[vol.Optional(param, default=default)] = selector.selector({"boolean": {}})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(fields),
            errors=errors,
        )
