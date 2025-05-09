"""Delta flash mode.

In delta flash mode, the existing firmware is first read back and compared to the new
one. Then, only flash pages which differ are erased and written.
"""

from itertools import batched
from typing import Iterable

from mcbootflash.protocol import BootAttrs, Chunk, Program, Page


def _xor_bytes(arg1: bytes, arg2: bytes) -> bytes:
    return int.to_bytes(int.from_bytes(arg1) ^ int.from_bytes(arg2), length=len(arg1))


def modified_pages(old: Program, new: Program, page_size: int) -> Iterable[int]:
    """Compare firmware versions and yield addresses of non-matching flash pages.

    Parameters
    ----------
    old : Program
        Start address and data of old firmware program.
    new : Program
        Start address and data of new firmware program.
    page_size : int
        Size of a flash page in bytes.

    Raises
    ------
    ValueError
        If old and new programs have mismatching start address or size.

    Yields
    ------
    int
        Start address of modified flash page.
    """
    if old.address != new.address:
        msg = (
            f"Program start addresses must be equal, got {old.address=}, {new.address=}"
        )
        raise ValueError(msg)

    if len(old.data) != len(new.data):
        msg = f"Program sizes must be equal, got {len(old.data)=}, {len(new.data)=}"
        raise ValueError(msg)

    for p1, p2 in zip(batched(old, page_size), batched(new, page_size)):
        if any(_xor_bytes(p1, p2)):
            yield p1.address
