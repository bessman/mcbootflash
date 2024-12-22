"""Flash firmware to devices running Microchip's 16-bit bootloader."""

from .error import (
    BadAddress,
    BadLength,
    BootloaderError,
    UnsupportedCommand,
    VerifyFail,
)
from .flash import (
    checksum,
    erase_flash,
    get_boot_attrs,
    read_flash,
    reset,
    self_verify,
    write_flash,
)
from .protocol import BootAttrs, Chunk, Command
from .util import chunked, readback

__all__ = [
    "BadAddress",
    "BadLength",
    "BootAttrs",
    "BootloaderError",
    "Chunk",
    "Command",
    "UnsupportedCommand",
    "VerifyFail",
    "checksum",
    "chunked",
    "erase_flash",
    "get_boot_attrs",
    "read_flash",
    "readback",
    "reset",
    "self_verify",
    "write_flash",
]

__version__ = "10.0.1"
