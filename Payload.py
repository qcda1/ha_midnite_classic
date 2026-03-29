"""Modbus Payload Builders.

Extracted from pymodbus 3.8.2 by Daniel Côté (2024-12-31).
Isolated because BinaryPayloadDecoder and BinaryPayloadBuilder were deprecated
and removed in pymodbus 3.9+.

Modified for ha_midnite_classic:
  - Endian class kept here (was also in pymodbus.constants — now removed in 3.11+)
  - No external pymodbus dependency
"""
from __future__ import annotations

__all__ = [
    "BinaryPayloadBuilder",
    "BinaryPayloadDecoder",
    "Endian",
]

from array import array
import enum
import logging
from struct import pack, unpack


# --------------------------------------------------------------------------- #
# Logging helper
# --------------------------------------------------------------------------- #
class Log:
    """Minimal logging wrapper."""

    _logger = logging.getLogger(__name__)

    @classmethod
    def debug(cls, txt, *args):
        if cls._logger.isEnabledFor(logging.DEBUG):
            cls._logger.debug(txt.format(*args), stacklevel=2)

    @classmethod
    def warning(cls, txt, *args):
        if cls._logger.isEnabledFor(logging.WARNING):
            cls._logger.warning(txt.format(*args), stacklevel=2)

    @classmethod
    def error(cls, txt, *args):
        if cls._logger.isEnabledFor(logging.ERROR):
            cls._logger.error(txt.format(*args), stacklevel=2)


# --------------------------------------------------------------------------- #
# Bit helpers
# --------------------------------------------------------------------------- #
def pack_bitstring(bits: list[bool]) -> bytes:
    ret = b""
    i = packed = 0
    for bit in bits:
        if bit:
            packed += 128
        i += 1
        if i == 8:
            ret += pack(">B", packed)
            i = packed = 0
        else:
            packed >>= 1
    if 0 < i < 8:
        packed >>= 7 - i
        ret += pack(">B", packed)
    return ret


def unpack_bitstring(data: bytes) -> list[bool]:
    bits = []
    for byte in data:
        value = int(byte)
        for _ in range(8):
            bits.append((value & 1) == 1)
            value >>= 1
    return bits


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #
class ModbusException(Exception):
    def __init__(self, string):
        self.string = string
        super().__init__(string)

    def __str__(self):
        return f"Modbus Error: {self.string}"

    def isError(self):
        return True


class ParameterException(ModbusException):
    def __init__(self, string=""):
        super().__init__(f"[Invalid Parameter] {string}")


# --------------------------------------------------------------------------- #
# Endian — previously in pymodbus.constants, removed in pymodbus 3.11
# --------------------------------------------------------------------------- #
class Endian(str, enum.Enum):
    """Byte / word endianness constants."""

    AUTO   = "@"
    BIG    = ">"
    LITTLE = "<"


# --------------------------------------------------------------------------- #
# BinaryPayloadBuilder
# --------------------------------------------------------------------------- #
class BinaryPayloadBuilder:
    """Build payload messages for modbus writes."""

    def __init__(self, payload=None, byteorder=Endian.LITTLE,
                 wordorder=Endian.BIG, repack=False):
        self._payload   = payload or []
        self._byteorder = byteorder
        self._wordorder = wordorder
        self._repack    = repack

    def _pack_words(self, fstring: str, value) -> bytes:
        value = pack(f"!{fstring}", value)
        if Endian.LITTLE in {self._byteorder, self._wordorder}:
            value = array("H", value)
            if self._byteorder == Endian.LITTLE:
                value.byteswap()
            if self._wordorder == Endian.LITTLE:
                value.reverse()
            value = value.tobytes()
        return value

    def encode(self) -> bytes:
        return b"".join(self._payload)

    def __str__(self) -> str:
        return self.encode().decode("utf-8")

    def reset(self) -> None:
        self._payload = []

    def to_registers(self):
        fstring = "!H"
        payload = self.build()
        if self._repack:
            payload = [unpack(self._byteorder + "H", v)[0] for v in payload]
        else:
            payload = [unpack(fstring, v)[0] for v in payload]
        return payload

    def to_coils(self) -> list[bool]:
        payload = self.to_registers()
        return [bool(int(bit)) for reg in payload for bit in format(reg, "016b")]

    def build(self) -> list[bytes]:
        buffer = self.encode()
        buffer += b"\x00" * (len(buffer) % 2)
        return [buffer[i: i + 2] for i in range(0, len(buffer), 2)]

    def add_8bit_uint(self, value: int) -> None:
        self._payload.append(pack(self._byteorder + "B", value))

    def add_16bit_uint(self, value: int) -> None:
        self._payload.append(pack(self._byteorder + "H", value))

    def add_32bit_uint(self, value: int) -> None:
        self._payload.append(self._pack_words("I", value))

    def add_64bit_uint(self, value: int) -> None:
        self._payload.append(self._pack_words("Q", value))

    def add_8bit_int(self, value: int) -> None:
        self._payload.append(pack(self._byteorder + "b", value))

    def add_16bit_int(self, value: int) -> None:
        self._payload.append(pack(self._byteorder + "h", value))

    def add_32bit_int(self, value: int) -> None:
        self._payload.append(self._pack_words("i", value))

    def add_64bit_int(self, value: int) -> None:
        self._payload.append(self._pack_words("q", value))

    def add_32bit_float(self, value: float) -> None:
        self._payload.append(self._pack_words("f", value))

    def add_64bit_float(self, value: float) -> None:
        self._payload.append(self._pack_words("d", value))

    def add_string(self, value: str) -> None:
        fstring = self._byteorder + str(len(value)) + "s"
        self._payload.append(pack(fstring, value.encode()))


# --------------------------------------------------------------------------- #
# BinaryPayloadDecoder
# --------------------------------------------------------------------------- #
class BinaryPayloadDecoder:
    """Decode payload messages from modbus responses."""

    def __init__(self, payload, byteorder=Endian.LITTLE, wordorder=Endian.BIG):
        self._payload   = payload
        self._pointer   = 0x00
        self._byteorder = byteorder
        self._wordorder = wordorder

    @classmethod
    def fromRegisters(cls, registers, byteorder=Endian.LITTLE, wordorder=Endian.BIG):
        Log.debug("registers:{}", registers)
        if isinstance(registers, list):
            payload = pack(f"!{len(registers)}H", *registers)
            return cls(payload, byteorder, wordorder)
        raise ParameterException("Invalid collection of registers supplied")

    @classmethod
    def fromCoils(cls, coils, byteorder=Endian.LITTLE, _wordorder=Endian.BIG):
        if isinstance(coils, list):
            payload = b""
            if padding := len(coils) % 8:
                coils = [False] * padding + coils
            for chunk in [coils[i: i + 8] for i in range(0, len(coils), 8)]:
                payload += pack_bitstring(chunk[::-1])
            return cls(payload, byteorder)
        raise ParameterException("Invalid collection of coils supplied")

    def _unpack_words(self, handle) -> bytes:
        if Endian.LITTLE in {self._byteorder, self._wordorder}:
            handle = array("H", handle)
            if self._byteorder == Endian.LITTLE:
                handle.byteswap()
            if self._wordorder == Endian.LITTLE:
                handle.reverse()
            handle = handle.tobytes()
        return handle

    def reset(self):
        self._pointer = 0x00

    def decode_8bit_uint(self):
        self._pointer += 1
        return unpack(self._byteorder + "B",
                      self._payload[self._pointer - 1: self._pointer])[0]

    def decode_bits(self, package_len=1):
        self._pointer += package_len
        return unpack_bitstring(self._payload[self._pointer - 1: self._pointer])

    def decode_16bit_uint(self):
        self._pointer += 2
        return unpack(self._byteorder + "H",
                      self._payload[self._pointer - 2: self._pointer])[0]

    def decode_32bit_uint(self):
        self._pointer += 4
        handle = self._unpack_words(self._payload[self._pointer - 4: self._pointer])
        return unpack("!I", handle)[0]

    def decode_64bit_uint(self):
        self._pointer += 8
        handle = self._unpack_words(self._payload[self._pointer - 8: self._pointer])
        return unpack("!Q", handle)[0]

    def decode_8bit_int(self):
        self._pointer += 1
        return unpack(self._byteorder + "b",
                      self._payload[self._pointer - 1: self._pointer])[0]

    def decode_16bit_int(self):
        self._pointer += 2
        return unpack(self._byteorder + "h",
                      self._payload[self._pointer - 2: self._pointer])[0]

    def decode_32bit_int(self):
        self._pointer += 4
        handle = self._unpack_words(self._payload[self._pointer - 4: self._pointer])
        return unpack("!i", handle)[0]

    def decode_64bit_int(self):
        self._pointer += 8
        handle = self._unpack_words(self._payload[self._pointer - 8: self._pointer])
        return unpack("!q", handle)[0]

    def decode_16bit_float(self):
        self._pointer += 2
        handle = self._unpack_words(self._payload[self._pointer - 2: self._pointer])
        return unpack("!e", handle)[0]

    def decode_32bit_float(self):
        self._pointer += 4
        handle = self._unpack_words(self._payload[self._pointer - 4: self._pointer])
        return unpack("!f", handle)[0]

    def decode_64bit_float(self):
        self._pointer += 8
        handle = self._unpack_words(self._payload[self._pointer - 8: self._pointer])
        return unpack("!d", handle)[0]

    def decode_string(self, size=1):
        self._pointer += size
        return self._payload[self._pointer - size: self._pointer]

    def skip_bytes(self, nbytes):
        self._pointer += nbytes
