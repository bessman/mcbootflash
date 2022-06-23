"""Flash firmware to devices running Microchip's 16-bit bootloader."""
from .connection import BootloaderConnection
from .error import (
    BadAddress,
    BadLength,
    BootloaderError,
    ChecksumError,
    McbootflashException,
    UnsupportedCommand,
    VerifyFail,
)
from .flashing import flash, get_parser
from .protocol import (
    FLASH_UNLOCK_KEY,
    BootCommand,
    BootResponse,
    ChecksumPacket,
    CommandPacket,
    MemoryRangePacket,
    ResponsePacket,
    VersionResponsePacket,
)

__all__ = [
    "BadAddress",
    "BadLength",
    "BootCommand",
    "BootResponse",
    "BootloaderConnection",
    "BootloaderError",
    "ChecksumError",
    "ChecksumPacket",
    "CommandPacket",
    "FLASH_UNLOCK_KEY",
    "McbootflashException",
    "MemoryRangePacket",
    "ResponsePacket",
    "UnsupportedCommand",
    "VerifyFail",
    "VersionResponsePacket",
    "flash",
    "get_parser",
]

__version__ = "2.0.0"
