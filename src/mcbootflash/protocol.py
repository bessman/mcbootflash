"""Definitions and representations for data sent to and from the bootloader."""
import enum
import struct
from dataclasses import asdict, dataclass
from typing import ClassVar, Type, TypeVar

from serial import Serial  # type: ignore[import]


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
        return cls(*struct.unpack(cls.FORMAT, data))

    @classmethod
    def from_serial(cls: Type[_P], interface: Serial) -> _P:
        """Create a Packet instance by reading from a serial interface."""
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

        | [ResponsePacket] | uint32        | uint32      |
        | [ResponsePacket] | program_start | program_end |

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

        | [ResponsePacket] | uint16   |
        | [ResponsePacket] | checksum |

    Parameters
    ----------
    checksum : uint16
        Checksum of `data_length` bytes starting from `address`.
    """

    checksum: int = 0
    FORMAT: ClassVar[str] = Response.FORMAT + "H"
