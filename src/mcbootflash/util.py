"""Utility functions."""

from collections.abc import Iterator
from typing import TextIO

import bincopy  # type: ignore[import-untyped]

from mcbootflash.flash import get_boot_attrs, read_flash
from mcbootflash.protocol import BootAttrs, Chunk, Command, Connection


def chunked(
    hexfile: str,
    boot_attrs: BootAttrs,
) -> tuple[int, Iterator[Chunk]]:
    """Split a HEX file into chunks.

    Parameters
    ----------
    hexfile : str
        Path of a HEX file containing application firmware.
    boot_attrs : BootAttrs
        The bootloader's attributes, as read by `get_boot_attrs`.

    Returns
    -------
    total_bytes : int
        The total number of bytes in all chunks.
    chunks : Iterator[Chunk]
        Appropriatelly sized chunks of data, suitable for writing in a loop with
        `write_flash`.

    Raises
    ------
    bincopy.Error
        If HEX file contains no data in program memory range.
    """
    hexdata = bincopy.BinFile()
    hexdata.add_microchip_hex_file(hexfile)
    hexdata.crop(*boot_attrs.memory_range)
    chunk_size = boot_attrs.max_packet_length - Command.size
    chunk_size -= chunk_size % boot_attrs.write_size
    chunk_size //= hexdata.word_size_bytes
    total_bytes = len(hexdata) * hexdata.word_size_bytes

    if total_bytes == 0:
        msg = "HEX file contains no data within program memory range"
        raise bincopy.Error(msg)

    total_bytes += (boot_attrs.write_size - total_bytes) % boot_attrs.write_size
    align = boot_attrs.write_size // hexdata.word_size_bytes
    return total_bytes, hexdata.segments.chunks(chunk_size, align, b"\xff\xff")


def readback(connection: Connection, outfile: TextIO) -> None:
    """Readback programmed application from flash memory.

    Parameters
    ----------
    connection : Connection
        Connection to device in bootloader mode.
    outfile : StringIO
        File-like object to write HEX data to.
    """
    boot_attrs = get_boot_attrs(connection)
    chunk_size = boot_attrs.max_packet_length - Command.size
    chunk_size -= chunk_size % boot_attrs.write_size
    word_size_bytes = 2
    chunk_size //= word_size_bytes
    address = boot_attrs.memory_range[0]
    binfile = bincopy.BinFile(word_size_bits=word_size_bytes * 8)

    while address + chunk_size < boot_attrs.memory_range[1]:
        data = read_flash(
            connection,
            address=address,
            size=chunk_size * word_size_bytes,
        )
        binfile.add_binary(data, address)
        address += chunk_size

    binfile.word_size_bytes = 1
    binfile.segments.word_size_bytes = 1

    for segment in binfile.segments:
        segment.word_size_bytes = 1

    outfile.write(binfile.as_ihex(number_of_data_bytes=16, address_length_bits=24))
