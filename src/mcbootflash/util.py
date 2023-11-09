"""Utility functions."""
from __future__ import annotations

from typing import Iterator

import bincopy  # type: ignore[import-not-found]

from mcbootflash.types import BootAttrs, Chunk, Command


def chunked(
    hexfile: str,
    bootattrs: BootAttrs,
) -> tuple[int, Iterator[Chunk]]:
    """Split a HEX file into chunks.

    Parameters
    ----------
    hexfile : str
        Path of a HEX file containing application firmare.
    bootattrs : BootAttrs
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
    ValueError
        If HEX file contains no data in program memory range.
    """
    hexdata = bincopy.BinFile()
    hexdata.add_microchip_hex_file(hexfile)
    hexdata.crop(*bootattrs.memory_range)
    chunk_size = bootattrs.max_packet_length - Command.get_size()
    chunk_size -= chunk_size % bootattrs.write_size
    chunk_size //= hexdata.word_size_bytes
    total_bytes = len(hexdata) * hexdata.word_size_bytes

    if not total_bytes:
        msg = "HEX file contains no data within program memory range"
        raise ValueError(msg)

    total_bytes += (bootattrs.write_size - total_bytes) % bootattrs.write_size
    align = bootattrs.write_size // hexdata.word_size_bytes
    return total_bytes, hexdata.segments.chunks(chunk_size, align, b"\x00\x00")
