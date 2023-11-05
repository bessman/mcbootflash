"""Flash firmware to devices running Microchip's 16-bit bootloader."""
from .error import (
    BadAddress,
    BadLength,
    BootloaderError,
    UnsupportedCommand,
    VerifyFail,
)
from .flash import (
    BootAttrs,
    checksum,
    chunked,
    erase_flash,
    get_boot_attrs,
    reset,
    self_verify,
    write_flash,
)

__all__ = [
    "BadAddress",
    "BadLength",
    "BootloaderError",
    "UnsupportedCommand",
    "VerifyFail",
    "BootAttrs",
    "checksum",
    "chunked",
    "erase_flash",
    "get_boot_attrs",
    "reset",
    "self_verify",
    "write_flash",
]

__version__ = "8.0.0"
