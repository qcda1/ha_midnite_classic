"""
Wrapper around classic_modbusdecoder.py — with connection instrumentation.

Changes vs. the previous version
--------------------------------
1. An explicit TCP probe runs before each Modbus read, so failures report the
   real ``errno`` (ENETUNREACH, EHOSTUNREACH, ECONNRESET, ETIMEDOUT…) instead
   of the opaque "getRegisters returned empty data".
2. Bounded retries with backoff: a short network outage (link flap, switch
   reboot) no longer turns into a hole in the recorder.
3. A ``ReadDiagnostics`` record the coordinator can log and expose.

``async_read_classic()`` keeps its previous signature and return contract
(``dict | None``), so existing callers such as config_flow are unaffected.
New code should prefer ``async_read_classic_ex()``, which also returns the
diagnostics.

Note for config_flow: pass ``attempts=1`` there so a bad host fails fast
instead of making the user wait through the retry sequence.
"""

from __future__ import annotations

import asyncio
import errno as errno_mod
import logging
import socket
import time
from dataclasses import asdict, dataclass
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Defaults tuned for a LAN where the link may drop for 10-20 s at a time.
# 3 attempts with a 2 s / 4 s backoff covers roughly 15 s of outage.
DEFAULT_ATTEMPTS = 3
DEFAULT_CONNECT_TIMEOUT = 3.0
DEFAULT_BACKOFF = 2.0


# Sentinel errors so config_flow can show a specific message
class ClassicModuleNotFoundError(Exception):
    """Raised when classic_modbusdecoder.py is missing from the integration folder."""


class ClassicConnectionError(Exception):
    """Raised when the Modbus TCP connection to the device fails."""


@dataclass
class ReadDiagnostics:
    """What actually happened during a read cycle."""

    host: str = ""
    port: int = 0
    attempts: int = 0
    duration_ms: float = 0.0
    success: bool = False
    tcp_ok: bool | None = None
    tcp_connect_ms: float | None = None
    err_no: int | None = None
    err_name: str | None = None
    error: str | None = None
    error_type: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def summary(self) -> str:
        """One-line human summary, used in log messages and UpdateFailed."""
        if self.success:
            return f"ok in {self.duration_ms:.0f} ms ({self.attempts} attempt(s))"

        parts: list[str] = [self.error_type or "error"]
        if self.err_no is not None:
            parts.append(f"errno={self.err_no} ({self.err_name or '?'})")
        if self.tcp_ok is False:
            parts.append("TCP error")
        elif self.tcp_ok is True and self.tcp_connect_ms is not None:
            parts.append(f"TCP OK in {self.tcp_connect_ms:.0f} ms")
        if self.error:
            parts.append(self.error)
        parts.append(f"{self.attempts} attempt(s) in {self.duration_ms:.0f} ms")
        return " — ".join(parts)


def _probe_tcp(
    host: str, port: int, timeout: float
) -> tuple[bool, float, int | None, str | None, str | None]:
    """Open and immediately close a TCP connection.

    Returns ``(ok, elapsed_ms, err_no, err_name, message)``. This is what
    distinguishes "the network is gone" (ENETUNREACH / EHOSTUNREACH) from
    "the Classic refused or reset us" (ECONNREFUSED / ECONNRESET) — a
    distinction the decoder swallows.
    """
    started = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
    except OSError as err:
        elapsed = (time.monotonic() - started) * 1000
        err_no = err.errno
        err_name = errno_mod.errorcode.get(err_no) if err_no is not None else None
        return False, elapsed, err_no, err_name, str(err)
    return True, (time.monotonic() - started) * 1000, None, None, None


def _read_classic_sync(host: str, port: int) -> dict[str, Any]:
    """Synchronous Modbus read — executed in a thread pool."""
    try:
        from .classic_modbusdecoder import getRegisters  # type: ignore[import]
    except ImportError as exc:
        raise ClassicModuleNotFoundError(
            "classic_modbusdecoder.py not found in the integration folder. "
            "Download it from https://github.com/qcda1/MidniteClassic and place it in "
            "custom_components/ha_midnite_classic/"
        ) from exc

    data = getRegisters(ip=host, port=port)

    if not data:
        raise ClassicConnectionError(
            f"getRegisters returned empty data for {host}:{port}"
        )

    return data


async def async_read_classic_ex(
    host: str,
    port: int,
    *,
    attempts: int = DEFAULT_ATTEMPTS,
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
    backoff: float = DEFAULT_BACKOFF,
) -> tuple[dict[str, Any] | None, ReadDiagnostics]:
    """Read all registers from a Midnite Classic, with retries and diagnostics.

    Returns ``(data, diagnostics)``; ``data`` is ``None`` on failure.

    Raises:
        ClassicModuleNotFoundError — if classic_modbusdecoder.py is missing.
    """
    loop = asyncio.get_running_loop()
    diag = ReadDiagnostics(host=host, port=port)
    started = time.monotonic()

    for attempt in range(1, max(1, attempts) + 1):
        diag.attempts = attempt

        ok, connect_ms, err_no, err_name, message = await loop.run_in_executor(
            None, _probe_tcp, host, port, connect_timeout
        )
        diag.tcp_ok = ok
        diag.tcp_connect_ms = connect_ms

        if not ok:
            diag.err_no = err_no
            diag.err_name = err_name
            diag.error = message
            diag.error_type = "TCPConnectError"
            _LOGGER.debug(
                "Classic %s:%s — attempt %d/%d: TCP failed in %.0f ms (errno=%s %s)",
                host,
                port,
                attempt,
                attempts,
                connect_ms,
                err_no,
                err_name or "?",
            )
        else:
            try:
                data = await loop.run_in_executor(
                    None, _read_classic_sync, host, port
                )
            except ClassicModuleNotFoundError:
                raise  # re-raise so config_flow can show a specific error
            except Exception as exc:  # noqa: BLE001
                exc_errno = getattr(exc, "errno", None)
                diag.err_no = exc_errno
                diag.err_name = (
                    errno_mod.errorcode.get(exc_errno)
                    if exc_errno is not None
                    else None
                )
                diag.error = str(exc)
                diag.error_type = type(exc).__name__
                _LOGGER.debug(
                    "Classic %s:%s — attempt %d/%d: TCP ok in %.0f ms but read failed — %s: %s",
                    host,
                    port,
                    attempt,
                    attempts,
                    connect_ms,
                    diag.error_type,
                    exc,
                )
            else:
                diag.success = True
                diag.err_no = None
                diag.err_name = None
                diag.error = None
                diag.error_type = None
                diag.duration_ms = (time.monotonic() - started) * 1000
                if attempt > 1:
                    _LOGGER.info(
                        "Classic %s:%s — read succeeded on attempt %d (%.0f ms total); "
                        "network outage absorbed",
                        host,
                        port,
                        attempt,
                        diag.duration_ms,
                    )
                return data, diag

        if attempt < attempts:
            await asyncio.sleep(backoff * attempt)

    diag.duration_ms = (time.monotonic() - started) * 1000
    return None, diag


async def async_read_classic(host: str, port: int, **kwargs: Any) -> dict[str, Any] | None:
    """Backwards-compatible wrapper.

    Returns:
        dict  — data from the device
        None  — connection/read error (logged)

    Raises:
        ClassicModuleNotFoundError — if classic_modbusdecoder.py is missing
    """
    data, diag = await async_read_classic_ex(host, port, **kwargs)
    if data is None:
        _LOGGER.error(
            "Error reading Classic at %s:%s — %s", host, port, diag.summary
        )
    return data
