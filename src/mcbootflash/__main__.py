"""Command line tool for flashing firmware."""
import argparse
import logging
import os
import time
from typing import Iterator, Tuple, Union

import bincopy  # type: ignore[import-untyped]
from serial import Serial  # type: ignore[import-untyped]

import mcbootflash as mcbf

_logger = logging.getLogger(__name__)


def parse() -> argparse.Namespace:
    """Parse arguments from command line.

    If `--version` is passed as an argument, print mcbootflash version and exit.

    Returns
    -------
    argparse.Namespace
        The returned Namespace contains the following arguments::

            file: str
            port: str
            baudrate: int
            timeout: float, default=5
            verbose: bool, default=False
            quiet: bool,  default=False
    """
    parser = argparse.ArgumentParser(
        description=(
            "Flash firmware over serial connection to a device running Microchip's "
            "16-bit bootloader."
        )
    )
    parser.add_argument(
        "file",
        type=str,
        help="An Intel HEX file containing application firmware.",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        required=True,
        help="Serial port connected to the device you want to flash.",
    )
    parser.add_argument(
        "-b",
        "--baudrate",
        type=int,
        required=True,
        help="Symbol rate of device's serial bus.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=5,
        help="Try to read data from the bus for this many seconds before giving up.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print debug messages.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress output.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{mcbf.__version__}",
    )

    return parser.parse_args()


class _Progress:
    def __init__(self) -> None:
        self._start = time.time()

    def print_progress(self, written_bytes: int, total_bytes: int) -> None:
        ratio = written_bytes / total_bytes
        percentage = f"{100 * ratio:.0f}%  "
        print(percentage, end="")
        digits = len(str(written_bytes))

        if digits < 4:
            data = f"{written_bytes} B "
        elif digits < 7:
            data = f"{written_bytes / 1024:.1f} KiB "
        else:
            data = f"{written_bytes / 1024**2:.1f} MiB "

        print(data, end="")
        elapsed = time.time() - self._start
        hours, minutes = divmod(elapsed, 3600)
        hours = int(hours)
        minutes, seconds = divmod(minutes, 60)
        minutes = int(minutes)
        seconds = int(seconds)
        timer = f" Elapsed Time: {hours}:{minutes:02}:{seconds:02}"
        self.print_bar(ratio, len(percentage) + len(data) + len(timer))
        print(timer, end="")
        print(end="\n" if written_bytes == total_bytes else "\r")

    @staticmethod
    def print_bar(ratio: float, used_width: int) -> None:
        try:
            bar_width = os.get_terminal_size().columns - used_width
            done = int(bar_width * ratio)
            left = bar_width - done
            progressbar = "|" + done * "#" + left * " " + "|"
            print(progressbar, end="")
        except OSError:
            # If get_terminal_size fails, skip the progressbar.
            pass


def main(args: Union[None, argparse.Namespace] = None) -> None:
    """Entry point for CLI."""
    args = args if args is not None else parse()
    _logconf(args.verbose, args.quiet)
    _logger.debug(f"mcbootflash {mcbf.__version__}")

    try:
        connection = Serial(
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
        )
        _logger.info("Connecting to bootloader...")
        bootattrs = mcbf.get_boot_attrs(connection)
        _logger.info("Connected")
        total_bytes, chunks = _chunks(args.file, bootattrs)
        connection.timeout *= 10
        mcbf.erase_flash(connection, bootattrs.memory_range, bootattrs.erase_size)
        connection.timeout /= 10
        _flash(connection, chunks, total_bytes, bootattrs, args.quiet)
        mcbf.self_verify(connection)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(
            "\nFlashing failed:",
            f"{type(exc).__name__}: {exc}" if str(exc) else f"{type(exc).__name__}",
        )
        logging.debug(exc, exc_info=True)


def _chunks(
    file: str, bootattrs: mcbf.BootAttrs
) -> Tuple[int, Iterator[bincopy.Segment]]:
    total_bytes, chunks = mcbf.chunks(file, bootattrs)

    if not chunks:
        raise mcbf.BootloaderError(
            "HEX file contains no data within program memory range"
        )

    return total_bytes, chunks


def _flash(
    connection: Serial,
    chunks: Iterator[bincopy.Segment],
    total_bytes: int,
    bootattrs: mcbf.BootAttrs,
    quiet: bool,
) -> None:
    has_checksum = True
    progress = _Progress() if not quiet else None
    written_bytes = 0

    for chunk in chunks:
        mcbf.write_flash(connection, chunk)
        if has_checksum:
            try:
                mcbf.checksum(connection, chunk, bootattrs.memory_range)
            except mcbf.UnsupportedCommand:
                _logger.warning("Bootloader does not support checksumming")
                has_checksum = False

        written_bytes += len(chunk)

        if progress is not None:
            progress.print_progress(written_bytes, total_bytes)


def _logconf(verbose: bool, quiet: bool) -> None:
    if not quiet:
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format="%(message)s",
        )

    if verbose:
        logging.basicConfig(level=logging.DEBUG)
