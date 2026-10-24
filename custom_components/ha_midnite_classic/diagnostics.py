"""Diagnostics support for Midnite Solar Classic.

Drop this file in ``custom_components/ha_midnite_classic/``. Home Assistant
picks it up automatically — no manifest change needed. The button appears
under Settings → Devices & Services → Midnite Classic → ⋮ → Download
diagnostics.

The output contains the last ERROR_HISTORY_SIZE failures with their real
errno, which is what you want to attach to a bug report or to correlate with
``dmesg`` link-flap timestamps.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import MidniteClassicCoordinator


def _collect_coordinators(stored: Any, seen: set[int] | None = None) -> list[MidniteClassicCoordinator]:
    """Find coordinators in whatever shape hass.data holds for this entry.

    Deliberately tolerant: the entry may store the coordinator directly, a
    dict of them, a list, or a runtime-data object holding one.
    """
    if seen is None:
        seen = set()
    if stored is None or id(stored) in seen:
        return []
    seen.add(id(stored))

    if isinstance(stored, MidniteClassicCoordinator):
        return [stored]

    found: list[MidniteClassicCoordinator] = []

    if isinstance(stored, dict):
        for value in stored.values():
            found.extend(_collect_coordinators(value, seen))
        return found

    if isinstance(stored, (list, tuple, set)):
        for value in stored:
            found.extend(_collect_coordinators(value, seen))
        return found

    for attr in ("coordinator", "coordinators", "classic", "classics"):
        if hasattr(stored, attr):
            found.extend(_collect_coordinators(getattr(stored, attr), seen))

    return found


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    stored = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if stored is None:
        stored = getattr(entry, "runtime_data", None)

    coordinators = _collect_coordinators(stored)

    return {
        "entry": {
            "title": entry.title,
            "version": entry.version,
            "options": dict(entry.options),
            # Host/port are LAN-only and are the whole point of the report,
            # so they are kept. No credentials are stored by this integration.
            "data": dict(entry.data),
        },
        "coordinators": [c.diagnostic_snapshot() for c in coordinators],
    }
