"""Flash firmware to devices running Microchip's 16-bit bootloader."""
from .connection import BootloaderConnection
from .error import (
    EXCEPTIONS,
    BadAddress,
    BadLength,
    BootloaderError,
    ChecksumError,
    UnsupportedCommand,
    VerifyFail,
)
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
    "BootloaderConnection",
    "BootloaderError",
    "ChecksumError",
    "UnsupportedCommand",
    "BadAddress",
    "BadLength",
    "VerifyFail",
    "EXCEPTIONS",
    "BootCommand",
    "BootResponse",
    "ChecksumPacket",
    "CommandPacket",
    "FLASH_UNLOCK_KEY",
    "MemoryRangePacket",
    "ResponsePacket",
    "VersionResponsePacket",
]

__version__ = "2.0.0"
