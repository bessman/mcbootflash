"""Utility functions."""

from collections.abc import Iterator

import bincopy  # type: ignore[import-untyped]

from mcbootflash.protocol import BootAttrs, Chunk, Command


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
