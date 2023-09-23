"""Definitions and representations for data sent to and from the bootloader."""
import enum
import logging
import struct
from dataclasses import asdict, dataclass
from typing import ClassVar, Dict, Type, TypeVar
from warnings import warn

from serial import Serial  # type: ignore[import]

from mcbootflash.error import (
    BadAddress,
    BadLength,
    BootloaderError,
    UnsupportedCommand,
    VerifyFail,
)

_logger = logging.getLogger(__name__)


class CommandCode(enum.IntEnum):
    """The MCC 16-bit bootloader supports these commands."""

    READ_VERSION = 0x00
    READ_FLASH = 0x01
    WRITE_FLASH = 0x02
    ERASE_FLASH = 0x03
    CALC_CHECKSUM = 0x08
    RESET_DEVICE = 0x09
    SELF_VERIFY = 0x0A
    GET_MEMORY_ADDRESS_RANGE = 0x0B


class ResponseCode(enum.IntEnum):
    """Sent by the bootloader in response to a command."""

    SUCCESS = 0x01
    UNSUPPORTED_COMMAND = 0xFF
    BAD_ADDRESS = 0xFE
    BAD_LENGTH = 0xFD
    VERIFY_FAIL = 0xFC


_P = TypeVar("_P", bound="Packet")


@dataclass
class Packet:
    """Base class for communication packets to and from the bootloader.

    Layout::

        | uint8   | uint16      | uint32          | uint32   |
        | command | data_length | unlock_sequence | address  |

    Parameters
    ----------
    command : CommandCode
        Command code which specifies which command should be executed by the bootloader.
    data_length : uint16
        Meaning depends on value of 'command'-field::

            WRITE_FLASH: Number of bytes following the command packet.
            ERASE_FLASH: Number of flash pages to be erased.
            CALC_CHECKSUM: Number of bytes to checksum.

        For other commands this field is ignored.
    unlock_sequence : uint32
        Key to unlock flash memory for writing. Write operations (WRITE_FLASH,
        ERASE_FLASH) will fail SILENTLY if this key is incorrect.
    address : uint32
        Address at which to perform command.
    FORMAT : ClassVar[str]
        Format string for `struct` which specifies types and layout of the data fields.

    Note
    ----
    No error is raised if the key is incorrect. A failed WRITE_FLASH operation
    can be detected by comparing checksums of the written bytes and the flash area
    they were written to. A failed ERASE_FLASH operation can be detected by issuing
    a SELF_VERIFY command. If the erase succeeded, SELF_VERIFY should return
    VERIFY_FAIL.
    """

    command: CommandCode
    data_length: int = 0
    unlock_sequence: int = 0
    address: int = 0
    FORMAT: ClassVar[str] = "=BH2I"

    def __bytes__(self) -> bytes:  # noqa: D105
        return struct.pack(self.FORMAT, *list(asdict(self).values()))

    @classmethod
    def from_bytes(cls: Type[_P], data: bytes) -> _P:
        """Create a Packet instance from a bytes-like object."""
        try:
            return cls(*struct.unpack(cls.FORMAT, data))
        except struct.error as exc:
            raise struct.error(
                f"{cls} expected {struct.calcsize(cls.FORMAT)} bytes, got {len(data)}"
            ) from exc

    @classmethod
    def from_serial(cls: Type[_P], interface: Serial) -> _P:
        """Create a Packet instance by reading from a serial interface."""
        warn(
            (
                "Packet.from_serial is deprecated and will be removed in a future "
                "version. Use get_response instead."
            ),
            DeprecationWarning,
        )
        return cls.from_bytes(interface.read(cls.get_size()))

    @classmethod
    def get_size(cls: Type[_P]) -> int:
        """Get the size of Packet in bytes."""
        return struct.calcsize(cls.FORMAT)


@dataclass
class Command(Packet):
    """Base class for packets sent to the bootloader.

    Layout is identical to Packet.
    """


@dataclass
class ResponseBase(Packet):
    """Base class for packets received from the bootloader.

    Layout is identical to Packet.
    """


@dataclass
class Version(ResponseBase):
    """Response to a READ_VERSION command.

    Layout::

        | [Packet] | uint16  | uint16            | uint16    | uint16    | ...
        | [Packet] | version | max_packet_length | (ignored) | device_id | ...

        ... | uint16    | uint16     | uint16     | uint32    | uint32    | uint32    |
        ... | (ignored) | erase_size | write_size | (ignored) | (ignored) | (ignored) |

    Parameters
    ----------
    version : uint16
        Bootloader version number.
    max_packet_length : int16
        Maximum number of bytes which can be sent to the bootloader per packet. Includes
        the size of the packet itself plus associated data.
    device_id : uint16
        A device-specific identifier.
    erase_size : uint16
        Size of a flash erase page in bytes. When erasing flash, the size of the memory
        area which should be erased is given in number of erase pages.
    write_size : uint16
        Size of a write block in bytes. When writing to flash, the data must align with
        a write block.
    """

    version: int = 0
    max_packet_length: int = 0
    device_id: int = 0
    erase_size: int = 0
    write_size: int = 0
    FORMAT: ClassVar[str] = Packet.FORMAT + "2H2xH2x2H12x"


@dataclass
class Response(ResponseBase):
    """Response to any command except READ_VERSION.

    Layout::

        | [Packet] | uint8   |
        | [Packet] | success |

    Parameters
    ----------
    success : ResponseCode
        Success or failure status of the command this packet is sent in response to.
    """

    success: ResponseCode = ResponseCode.UNSUPPORTED_COMMAND
    FORMAT: ClassVar[str] = Packet.FORMAT + "B"


@dataclass
class MemoryRange(Response):
    """Response to GET_MEMORY_RANGE command.

    Layout::

        | [Response] | uint32        | uint32      |
        | [Response] | program_start | program_end |

    Parameters
    ----------
    program_start : uint32
        Low end of address space to which application firmware can be flashed.
    program_end : uint32
        High end of address space to which application firmware can be flashed.
    """

    program_start: int = 0
    program_end: int = 0
    FORMAT: ClassVar[str] = Response.FORMAT + "2I"


@dataclass
class Checksum(Response):
    """Response to CALCULATE_CHECKSUM command.

    Layout::

        | [Response] | uint16   |
        | [Response] | checksum |

    Parameters
    ----------
    checksum : uint16
        Checksum of `data_length` bytes starting from `address`.
    """

    checksum: int = 0
    FORMAT: ClassVar[str] = Response.FORMAT + "H"


def get_response(interface: Serial, in_response_to: Command) -> ResponseBase:
    """Get a Response packet from a serial connection.

    Parameters
    ----------
    interface : Serial
        An open Serial instance.
    in_response_to : Command
        The most recently sent Command packet.

    Returns
    -------
    packet : ResponseBase
        An instance of a ResponseBase packet or a subclass thereof.
    """
    # Can't read the whole response in one go. Its length depends on whether it's an
    # error or not. Start by reading the command echo to determine the response type.
    response = ResponseBase.from_bytes(interface.read(ResponseBase.get_size()))
    _logger.debug(_format_rx(bytes(response)))

    if response.command != in_response_to.command:
        raise BootloaderError("Command code mismatch")

    response_type_map: Dict[CommandCode, Type[ResponseBase]] = {
        CommandCode.READ_VERSION: Version,
        CommandCode.READ_FLASH: Response,
        CommandCode.WRITE_FLASH: Response,
        CommandCode.ERASE_FLASH: Response,
        CommandCode.CALC_CHECKSUM: Checksum,
        CommandCode.RESET_DEVICE: Response,
        CommandCode.SELF_VERIFY: Response,
        CommandCode.GET_MEMORY_ADDRESS_RANGE: MemoryRange,
    }
    response_type = response_type_map[CommandCode(response.command)]

    # READ_VERSION has no 'success' flag.
    if response_type is Version:
        remainder = interface.read(response_type.get_size() - response.get_size())
        _logger.debug(_format_rx(remainder, bytes(response)))
        return response_type.from_bytes(bytes(response) + remainder)

    success = interface.read(1)
    _logger.debug(_format_rx(success, bytes(response)))

    if success[0] != ResponseCode.SUCCESS:
        bootloader_exceptions: Dict[ResponseCode, Type[BootloaderError]] = {
            ResponseCode.UNSUPPORTED_COMMAND: UnsupportedCommand,
            ResponseCode.BAD_ADDRESS: BadAddress,
            ResponseCode.BAD_LENGTH: BadLength,
            ResponseCode.VERIFY_FAIL: VerifyFail,
        }
        raise bootloader_exceptions[success[0]]

    response = Response.from_bytes(bytes(response) + success)
    remainder = interface.read(response_type.get_size() - response.get_size())

    if remainder:
        _logger.debug(_format_rx(remainder, bytes(response)))

    response = response_type.from_bytes(bytes(response) + remainder)

    return response


def _format_rx(rxbytes: bytes, pad: bytes = b"") -> str:
    padding = " " * len(f"{' '.join(f'{b:02X}' for b in pad)}")
    padding += " " if padding else ""
    return f"RX: {padding}{' '.join(f'{b:02X}' for b in rxbytes)}"
