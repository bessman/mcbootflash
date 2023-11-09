"""These functions are used to communicate with the bootloader."""
from __future__ import annotations

import logging

try:
    # New in python 3.12.
    from itertools import batched
except ImportError:  # pragma: no cover
    from itertools import islice
    from typing import no_type_check

    # fmt: off
    @no_type_check  # type: ignore[no-redef]
    def batched(iterable, n):  # noqa: ANN001,ANN201,D103
        # batched('ABCDEFG', 3) --> ABC DEF G
        if n < 1:
            raise ValueError("n must be at least one")  # noqa: TRY003,EM101
        it = iter(iterable)
        while batch := tuple(islice(it, n)):
            yield batch
    # fmt: on


from mcbootflash.error import (
    BadAddress,
    BadLength,
    BootloaderError,
    UnsupportedCommand,
    VerifyFail,
)
from mcbootflash.types import (
    BootAttrs,
    Checksum,
    Chunk,
    Command,
    CommandCode,
    Connection,
    MemoryRange,
    Response,
    ResponseBase,
    ResponseCode,
    Version,
)

_logger = logging.getLogger(__name__)
_FLASH_UNLOCK_KEY = 0x00AA0055


def get_boot_attrs(connection: Connection) -> BootAttrs:
    """Read bootloader attributes.

    Parameters
    ----------
    connection : Connection
        Connection to device in bootloader mode.

    Returns
    -------
    : BootAttrs
    """
    (
        version,
        max_packet_length,
        device_id,
        erase_size,
        write_size,
    ) = _read_version(connection)
    memory_range = _get_memory_address_range(connection)

    try:
        _get_remote_checksum(connection, memory_range[0], write_size)
        has_checksum = True
    except UnsupportedCommand:
        _logger.warning("Bootloader does not support checksumming")
        has_checksum = False

    return BootAttrs(
        version,
        max_packet_length,
        device_id,
        erase_size,
        write_size,
        memory_range,
        has_checksum,
    )


def _read_version(connection: Connection) -> tuple[int, int, int, int, int]:
    """Read bootloader version and some other useful information.

    Parameters
    ----------
    connection : Connection
        Connection to device in bootloader mode.

    Returns
    -------
    version : int
    max_packet_length : int
        The maximum size of a single packet sent to the bootloader,
        including both the command and associated data.
    device_id : int
    erase_size : int
        Flash page size. When erasing flash memory, the number of bytes to
        be erased must align with a flash page.
    write_size : int
        Write block size. When writing to flash, the number of bytes to be
        written must align with a write block.
    """
    read_version_response = _send_and_receive(
        connection,
        Command(CommandCode.READ_VERSION),
    )

    assert isinstance(read_version_response, Version)

    _logger.debug("Got bootloader attributes:")
    _logger.debug(f"Max packet length: {read_version_response.max_packet_length}")
    _logger.debug(f"Erase size:        {read_version_response.erase_size}")
    _logger.debug(f"Write size:        {read_version_response.write_size}")

    return (
        read_version_response.version,
        read_version_response.max_packet_length,
        read_version_response.device_id,
        read_version_response.erase_size,
        read_version_response.write_size,
    )


def _get_memory_address_range(connection: Connection) -> tuple[int, int]:
    """Get the program memory range, i.e. the range of writable addresses.

    Parameters
    ----------
    connection : Connection
        Connection to device in bootloader mode.

    Returns
    -------
    memory_range_low_end : int
    memory_range_high_end : int

    The returned tuple is suitable for use in `range`, i.e. the upper bound is not
    part of the writable range.
    """
    mem_range_response = _send_and_receive(
        connection,
        Command(CommandCode.GET_MEMORY_ADDRESS_RANGE),
    )

    assert isinstance(mem_range_response, MemoryRange)

    _logger.debug(
        "Got program memory range: "
        f"{mem_range_response.program_start:#08x}:"
        f"{mem_range_response.program_end:#08x}",
    )
    # program_end + 2 explanation:
    # +1 because the upper bound reported by the bootloader is inclusive, but we
    # want to use it as a Python range, which is half-open.
    # +1 because the final byte of the final 24-bit instruction is not included in
    # the range reported by the bootloader, but it is still writable.
    return mem_range_response.program_start, mem_range_response.program_end + 2


def erase_flash(
    connection: Connection,
    erase_range: tuple[int, int],
    erase_size: int,
) -> None:
    """Erase program memory area.

    Note
    ----
    Erasing a large memory area can take several seconds. Set the connection timeout
    accordingly.

    Parameters
    ----------
    connection:  Connection
        Connection to device in bootloader mode.
    erase_range : tuple[int, int]
        Tuple of addresses forming a range to erase. The range is half-open,
        [start, end), i.e. the second address in the tuple is not erased.
    erase_size : int
        Size of a flash page, i.e. the smallest number of bytes which can be atomically
        erased.

    Raises
    ------
    ValueError
        If `erase_range[1] - erase_range[0]` is not a multiple of `erase_size`.
    """
    start, end = erase_range

    if (end - start) % erase_size:
        msg = "Address range is not a multiple of erase size"
        raise ValueError(msg)

    _logger.debug(f"Erasing addresses {start:#08x}:{end:#08x}")
    _send_and_receive(
        connection,
        command=Command(
            command=CommandCode.ERASE_FLASH,
            data_length=(end - start) // erase_size,
            unlock_sequence=_FLASH_UNLOCK_KEY,
            address=start,
        ),
    )


def write_flash(connection: Connection, chunk: Chunk) -> None:
    """Write data to bootloader.

    Parameters
    ----------
    connection : Connection
        Connection to device in bootloader mode.
    chunk : Chunk
        Firmware chunk to write to bootloader.
    """
    _logger.debug(f"Writing {len(chunk.data)} bytes to {chunk.address:#08x}")
    _send_and_receive(
        connection,
        Command(
            command=CommandCode.WRITE_FLASH,
            data_length=len(chunk.data),
            unlock_sequence=_FLASH_UNLOCK_KEY,
            address=chunk.address,
        ),
        chunk.data,
    )


def self_verify(connection: Connection) -> None:
    """Check if an application is installed.

    Parameters
    ----------
    connection : Connection
        Connection to device in bootloader mode.

    Raises
    ------
    mcbootflash.VerifyFail
        If no application is detected.
    """
    _send_and_receive(connection, Command(command=CommandCode.SELF_VERIFY))


def checksum(
    connection: Connection,
    chunk: Chunk,
) -> None:
    """Compare checksums calculated locally and onboard device.

    Parameters
    ----------
    connection : Connection
        Connection to device in bootloader mode.
    chunk : Chunk
        Firmware chunk to checksum.

    Raises
    ------
    BootloaderError
        If checksums do not match.
    """
    checksum1 = _get_local_checksum(chunk.data)
    checksum2 = _get_remote_checksum(connection, chunk.address, len(chunk.data))

    if checksum1 != checksum2:
        _logger.debug(f"Checksum mismatch: {checksum1} != {checksum2}")
        _logger.debug("unlock_sequence field may be incorrect")
        msg = "Checksum mismatch"
        raise BootloaderError(msg)

    _logger.debug(f"Checksum OK: {checksum1}")


def _get_remote_checksum(connection: Connection, address: int, length: int) -> int:
    checksum_response = _send_and_receive(
        connection,
        Command(
            command=CommandCode.CALC_CHECKSUM,
            data_length=length,
            address=address,
        ),
    )
    assert isinstance(checksum_response, Checksum)
    return checksum_response.checksum


def _get_local_checksum(data: bytes) -> int:
    chksum = 0
    extended_address_width = 4

    for batch in batched(data, extended_address_width):
        chksum += batch[0] + (batch[1] << 8) + batch[2]

    return chksum & 0xFFFF


def reset(connection: Connection) -> None:
    """Reset device.

    Parameters
    ----------
    connection : Connection
        Connection to device in bootloader mode.
    """
    _send_and_receive(connection, Command(command=CommandCode.RESET_DEVICE))
    _logger.debug("Device reset")


def _read_flash() -> None:
    raise NotImplementedError


def _get_response(connection: Connection, in_response_to: Command) -> ResponseBase:
    """Get a Response packet.

    Parameters
    ----------
    connection : Connection
        Connection to device in bootloader mode.
    in_response_to: Command
        The `Command` to which a response is expected.

    Returns
    -------
    packet : ResponseBase
        An instance of a ResponseBase packet or a subclass thereof.
    """
    # Can't read the whole response in one go. Its length depends on whether it's an
    # error or not. Start by reading the command echo to determine the response
    # type.
    response = ResponseBase.from_bytes(connection.read(ResponseBase.get_size()))
    _logger.debug(f"RX: {_format_debug_bytes(bytes(response))}")

    if response.command != in_response_to.command:
        msg = "Command code mismatch"
        raise BootloaderError(msg)

    response_type_map: dict[CommandCode, type[ResponseBase]] = {
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
        remainder = connection.read(response_type.get_size() - response.get_size())
        _logger.debug(f"RX: {_format_debug_bytes(remainder, bytes(response))}")
        return response_type.from_bytes(bytes(response) + remainder)

    success = connection.read(1)
    _logger.debug(f"RX: {_format_debug_bytes(success, bytes(response))}")

    if success[0] != ResponseCode.SUCCESS:
        bootloader_exceptions: dict[ResponseCode, type[BootloaderError]] = {
            ResponseCode.UNSUPPORTED_COMMAND: UnsupportedCommand,
            ResponseCode.BAD_ADDRESS: BadAddress,
            ResponseCode.BAD_LENGTH: BadLength,
            ResponseCode.VERIFY_FAIL: VerifyFail,
        }
        raise bootloader_exceptions[ResponseCode(success[0])]

    response = Response.from_bytes(bytes(response) + success)
    remainder = connection.read(response_type.get_size() - response.get_size())

    if remainder:
        _logger.debug(f"RX: {_format_debug_bytes(remainder, bytes(response))}")

    return response_type.from_bytes(bytes(response) + remainder)


def _send_and_receive(
    connection: Connection,
    command: Command,
    data: bytes = b"",
) -> ResponseBase:
    msg = f"TX: {_format_debug_bytes(bytes(command))}"
    msg += f" plus {len(data)} data bytes" if data else ""
    _logger.debug(msg)
    connection.write(bytes(command) + data)
    return _get_response(connection, command)


def _format_debug_bytes(debug_bytes: bytes, pad: bytes = b"") -> str:
    padding = " " * len(pad) * 3
    return f"{padding}{' '.join(f'{b:02X}' for b in debug_bytes)}"
