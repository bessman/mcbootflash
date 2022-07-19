"""Flash firmware to devices running Microchip's 16-bit bootloader."""
from .connection import BootloaderConnection
from .error import (
    BadAddress,
    BadLength,
    BootloaderError,
    ChecksumError,
    ConnectionFailure,
    FlashEraseFail,
    McbootflashException,
    NoData,
    UnexpectedResponse,
    UnsupportedCommand,
    VerifyFail,
)
from .flashing import flash, get_parser
from .protocol import (
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
    "ConnectionFailure",
    "FlashEraseFail",
    "McbootflashException",
    "MemoryRangePacket",
    "NoData",
    "ResponsePacket",
    "UnexpectedResponse",
    "UnsupportedCommand",
    "VerifyFail",
    "VersionResponsePacket",
    "flash",
    "get_parser",
]

__version__ = "4.1.0"
