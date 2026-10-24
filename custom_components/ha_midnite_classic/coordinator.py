"""DataUpdateCoordinator for Midnite Solar Classic."""

from __future__ import annotations

import logging
from collections import deque
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .classic_reader import (
    DEFAULT_ATTEMPTS,
    DEFAULT_BACKOFF,
    DEFAULT_CONNECT_TIMEOUT,
    async_read_classic_ex,
)
from .classic_writer import WriteResult, write_register
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

#: How many past failures to keep for the diagnostics download.
ERROR_HISTORY_SIZE = 20


class MidniteClassicCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls one Midnite Classic controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        scan_interval: int,
        device_name: str,
        *,
        read_attempts: int = DEFAULT_ATTEMPTS,
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
        retry_backoff: float = DEFAULT_BACKOFF,
    ) -> None:
        self.host = host
        self.port = port
        self.device_name = device_name

        # Read tuning — see classic_reader for the defaults' rationale.
        self.read_attempts = read_attempts
        self.connect_timeout = connect_timeout
        self.retry_backoff = retry_backoff

        # Health counters, surfaced by diagnostics.py and by the optional
        # diagnostic sensors.
        self.consecutive_errors: int = 0
        self.total_errors: int = 0
        self.total_reads: int = 0
        self.last_success: datetime | None = None
        self.last_error: str | None = None
        self.last_error_at: datetime | None = None
        self.last_read_ms: float | None = None
        self.error_history: deque[dict[str, Any]] = deque(maxlen=ERROR_HISTORY_SIZE)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{host}",
            update_interval=timedelta(seconds=scan_interval),
        )

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Classic controller."""
        data, diag = await async_read_classic_ex(
            self.host,
            self.port,
            attempts=self.read_attempts,
            connect_timeout=self.connect_timeout,
            backoff=self.retry_backoff,
        )

        self.total_reads += 1
        self.last_read_ms = diag.duration_ms

        if data is None:
            now = dt_util.utcnow()
            self.consecutive_errors += 1
            self.total_errors += 1
            self.last_error = diag.summary
            self.last_error_at = now
            self.error_history.append({"at": now.isoformat(), **diag.as_dict()})

            _LOGGER.warning(
                "Classic %s (%s:%s): failure #%d — %s — last success: %s",
                self.device_name,
                self.host,
                self.port,
                self.consecutive_errors,
                diag.summary,
                self._since_last_success(),
            )
            raise UpdateFailed(
                f"Failed to read data from Midnite Classic at "
                f"{self.host}:{self.port} — {diag.summary}"
            )

        if self.consecutive_errors:
            _LOGGER.info(
                "Classic %s (%s:%s): recovered after %d consecutive failure(s)",
                self.device_name,
                self.host,
                self.port,
                self.consecutive_errors,
            )

        self.consecutive_errors = 0
        self.last_success = dt_util.utcnow()
        return data

    # ------------------------------------------------------------------
    # Health reporting
    # ------------------------------------------------------------------

    def _since_last_success(self) -> str:
        if self.last_success is None:
            return "never since startup"
        delta = dt_util.utcnow() - self.last_success
        return f"for {delta.total_seconds():.0f} seconds"

    @property
    def success_rate(self) -> float | None:
        """Share of successful polls since startup, 0-1."""
        if not self.total_reads:
            return None
        return (self.total_reads - self.total_errors) / self.total_reads

    def diagnostic_snapshot(self) -> dict[str, Any]:
        """Health summary — consumed by diagnostics.py and diagnostic sensors."""
        return {
            "device_name": self.device_name,
            "host": self.host,
            "port": self.port,
            "scan_interval_s": (
                self.update_interval.total_seconds() if self.update_interval else None
            ),
            "read_attempts": self.read_attempts,
            "connect_timeout_s": self.connect_timeout,
            "retry_backoff_s": self.retry_backoff,
            "total_reads": self.total_reads,
            "total_errors": self.total_errors,
            "consecutive_errors": self.consecutive_errors,
            "success_rate": self.success_rate,
            "last_read_ms": self.last_read_ms,
            "last_success": (
                self.last_success.isoformat() if self.last_success else None
            ),
            "last_error": self.last_error,
            "last_error_at": (
                self.last_error_at.isoformat() if self.last_error_at else None
            ),
            "last_update_success": self.last_update_success,
            "error_history": list(self.error_history),
        }

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

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
