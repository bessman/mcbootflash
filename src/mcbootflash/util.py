"""Utility functions."""

import logging

import bincopy  # type: ignore[import-untyped]

from mcbootflash.flash import (
    checksum,
    get_boot_attrs,
    erase_flash,
    read_flash,
    write_flash,
)
from mcbootflash.protocol import BootAttrs, ChunkProtocol, Connection

_logger = logging.getLogger(__name__)


def _chunked(
    records: str,
    memory_range: tuple[int, int],
    chunk_size: int,
    align: int,
) -> list[ChunkProtocol]:
    hexdata = bincopy.BinFile()
    hexdata.add_microchip_hex(records)
    hexdata.crop(*memory_range)
    chunk_size = chunk_size // hexdata.word_size_bytes
    align = align // hexdata.word_size_bytes
    return list(hexdata.segments.chunks(chunk_size, align, b"\xff\xff"))


def chunked(
    records: str,
    boot_attrs: BootAttrs,
) -> list[ChunkProtocol]:
    """Split firmware into writable chunks.

    Parameters
    ----------
    records : str
        Firmware HEX file records.
    boot_attrs : BootAttrs
        The bootloader's attributes, as read by `get_boot_attrs`.

    Returns
    -------
    chunks : list[Chunk]
        Appropriatelly sized chunks of data, suitable for writing in a loop with
        `write_flash`.
    """
    return _chunked(
        records,
        boot_attrs.memory_range,
        boot_attrs.max_packet_length,
        boot_attrs.write_size,
    )


def pages(
    records: str,
    boot_attrs: BootAttrs,
) -> list[ChunkProtocol]:
    """Split firmware into flash page-sized chunks.

    Parameters
    ----------
    records : str
        Firmware HEX records.
    boot_attrs : BootAttrs
        The bootloader's attributes, as read by `get_boot_attrs`.

    Returns
    -------
    pages : list[Chunk]
        Chunks of data corresponding to atomically erasable flash pages.
    """
    return _chunked(
        records,
        boot_attrs.memory_range,
        boot_attrs.erase_size,
        boot_attrs.erase_size,
    )


def delta_erase(connection: Connection, new_records: str) -> None:
    """Only erase flash pages which differ from the to-be-flashed firmware image.

    Parameters
    ----------
    connection : Connection
        Connection to dvice in bootloader mode.
    new_records : str
        Firmware HEX records.
    """
    _logger.debug("Delta erasing program area...")
    boot_attrs = get_boot_attrs(connection)
    old_records = readback(connection)
    new_pages = pages(new_records, boot_attrs)
    old_pages = pages(old_records, boot_attrs)
    to_erase: list[tuple[int, int]] = []
    to_write: list[ChunkProtocol] = []

    for new, old in zip(new_pages, old_pages):
        if _need_erase(old.data, new.data):
            erase_range = new.address, new.address + boot_attrs.erase_size // 2
            to_erase.append(erase_range)
            to_write.append()

    _logger.debug(f"{len(to_erase)} / {len(new_pages)} pages need to be erased")

    for page in to_erase:
        erase_flash(connection, page, boot_attrs.erase_size)


def _need_erase(old_page_data: bytes, new_page_data: bytes) -> bool:
    # EEPROM can be flipped from 0 to 1 by erase, and from 1 to 0 by write. It is
    # necessary to erase before write if the new data contains any 1-bits in a position
    # where the old data has a 0-bit
    # This amounts to checking bitwise material nonimplication between the new and old
    # data. If any bits in the new data NIMPLY the same bits in the old data, the page
    # to which those bits belong must be erased before write.
    old = int.from_bytes(old_page_data)
    new = int.from_bytes(new_page_data)
    return not (~new | old)


def delta_write(
    connection: Connection, new_records: str, verify_checksum: bool = False
) -> None:
    _logger.debug("Delta writing new firmware...")
    boot_attrs = get_boot_attrs(connection)
    old_records = readback(connection)
    new_chunks = chunked(new_records, boot_attrs)
    old_chunks = chunked(old_records, boot_attrs)
    to_write: list[ChunkProtocol] = []

    for new, old in zip(new_chunks, old_chunks):
        if old.data != new.data:
            to_write.append(new)

    to_write_bytes = len(to_write) * boot_attrs.max_data_length
    total_bytes = len(new_chunks) * boot_attrs.max_data_length
    _logger.debug(f"Need to write {to_write_bytes} / {total_bytes} bytes.")

    for chunk in to_write:
        write_flash(connection, chunk)

        if verify_checksum:
            checksum(connection, chunk)


def readback(connection: Connection) -> str:
    """Readback programmed application from flash memory.

    Parameters
    ----------
    connection : Connection
        Connection to device in bootloader mode.

    Returns
    -------
    records : str
        Hex file records.
    """
    boot_attrs = get_boot_attrs(connection)
    word_size_bytes = 2
    binfile = bincopy.BinFile(word_size_bits=word_size_bytes * 8)

    for address in range(
        *boot_attrs.memory_range,
        boot_attrs.max_packet_length // word_size_bytes,
    ):
        data = read_flash(connection, address, boot_attrs.max_packet_length)
        binfile.add_binary(data, address)

    return binfile.as_microchip_hex(number_of_data_bytes=16, address_length_bits=24)
