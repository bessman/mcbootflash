"""Custom types used by mcbootflash."""
from __future__ import annotations

import enum
import struct
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:  # pragma: no cover
    from typing_extensions import Self


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


@dataclass
class Packet:
    """Base class for communication packets to and from the bootloader.

    Layout:

        | uint8   | uint16      | uint32          | uint32   |
        | command | data_length | unlock_sequence | address  |

    Parameters
    ----------
    command : CommandCode
        Command code which specifies which command should be executed by the bootloader.
    data_length : uint16
        Meaning depends on value of 'command'-field:

            WRITE_FLASH: Number of bytes following the command packet.
            ERASE_FLASH: Number of flash pages to be erased.
            CALC_CHECKSUM: Number of bytes to checksum.

        For other commands this field is ignored.
    unlock_sequence : uint32
        Key to unlock flash memory for writing. Write operations (`WRITE_FLASH`,
        `ERASE_FLASH`) will fail SILENTLY if this key is incorrect.
    address : uint32
        Address at which to perform command.
    FORMAT : ClassVar[str]
        Format string for `struct` which specifies types and layout of the data fields.

    Note
    ----
    No error is raised if `unlock_sequence` is incorrect. A failed `WRITE_FLASH`
    operation can be detected by comparing checksums of the written bytes and the flash
    area they were written to. A failed ERASE_FLASH operation can be detected by issuing
    a `SELF_VERIFY` command. If the erase succeeded, `SELF_VERIFY` should return
    `VERIFY_FAIL`.
    """

    command: CommandCode
    data_length: int = 0
    unlock_sequence: int = 0
    address: int = 0
    FORMAT: ClassVar[str] = "=BH2I"

    def __bytes__(self) -> bytes:  # noqa: D105
        return struct.pack(self.FORMAT, *list(asdict(self).values()))

    @classmethod
    def from_bytes(cls: type[Self], data: bytes) -> Self:
        """Create a Packet instance from a bytes-like object."""
        try:
            return cls(*struct.unpack(cls.FORMAT, data))
        except struct.error as exc:
            msg = f"{cls} expected {struct.calcsize(cls.FORMAT)} bytes, got {len(data)}"
            raise struct.error(msg) from exc

    @classmethod
    def get_size(cls: type[Self]) -> int:
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
    """Response to a `READ_VERSION` command.

    Layout::

        | [Packet] | uint16  | uint16            | uint16    | uint16    | ...
        | [Packet] | version | max_packet_length | (ignored) | device_id | ...

        ... | uint16    | uint16     | uint16     | uint32    | uint32    | uint32    |
        ... | (ignored) | erase_size | write_size | (ignored) | (ignored) | (ignored) |

    Parameters
    ----------
    version : uint16
        Bootloader version number.
    max_packet_length : uint16
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
    """Response to any command except `READ_VERSION`.

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
    """Response to `GET_MEMORY_RANGE` command.

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
    """Response to `CALCULATE_CHECKSUM` command.

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


@dataclass
class BootAttrs:
    """Bootloader attributes.

    Parameters
    ----------
    version : int
        Bootloader version number.
    max_packet_length : int
        Maximum number of bytes which can be sent to the bootloader per packet. Includes
        the size of the packet itself plus associated data.
    device_id : int
        A device-specific identifier.
    erase_size : int
        Size of a flash erase page in bytes. When erasing flash, the size of the memory
        area which should be erased is given in number of erase pages.
    write_size : int
        Size of a write block in bytes. When writing to flash, the data must align with
        a write block.
    memory_range : tuple[int, int]
        Tuple of addresses specifying the program memory range. The range is half-open,
        i.e. the upper address is not part of the program memory range.
    has_checksum : bool
        Indicates whether or not the bootloader supports the `CALC_CHECKSUM` command.
    """

    version: int
    max_packet_length: int
    device_id: int
    erase_size: int
    write_size: int
    memory_range: tuple[int, int]
    has_checksum: bool


class Chunk(Protocol):
    """A piece of a firmware image.

    `mcbootflash.chunked` can be used to generate correctly aligned and sized chunks
    from a HEX file.

    Attributes
    ----------
    address : int
        The address associated with the start of the data. Must be aligned with (i.e. be
        a multiple of) the bootloader's `write_size` attribute.
    data : bytes
        Data to be written to the bootloader. The data length be a multiple of the
        bootloader's `write_size` attribute, and must be no longer than the bootloader's
        `max_packet_length` attribute minus the size of the command packet header (which
        can be gotten with `Command.get_size`).
    """

    address: int
    data: bytes


class Connection(Protocol):
    """Anything that can read and write bytes from/to the bootloader.

    Typically, this is an open [`serial.Serial`](https://pyserial.readthedocs.io/en/latest/pyserial_api.html#serial.Serial)
    instance.
    """

    def read(self, size: int = 1) -> bytes:
        """Read bytes from the bootloader.

        Parameters
        ----------
        size : int, default=1
            Number of bytes to read.

        Returns
        -------
        data : bytes
            Bytes read from the bootloader.
        """
        ...  # pragma: no cover

    def write(self, data: bytes) -> int:
        """Write bytes to the bootloader.

        Parameters
        ----------
        data : bytes
            Bytes to write to the bootloader.

        Returns
        -------
        size : int
            Number of bytes written to the bootloader.
        """
        ...  # pragma: no cover
