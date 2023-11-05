"""Command line tool for flashing firmware."""
import argparse
import logging
import shutil
import time
from typing import Iterator, Union

import bincopy  # type: ignore[import-untyped]
from serial import Serial  # type: ignore[import-untyped]

import mcbootflash as mcbf

_logger = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    """Parse arguments from command line.

    If `--version` is passed as an argument, print mcbootflash version and exit.

    Returns
    -------
    argparse.Namespace
        The returned ArgumentParser contains the following arguments::

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

    return parser


def main(args: Union[None, argparse.Namespace] = None) -> None:
    """Entry point for CLI."""
    args = args if args is not None else get_parser().parse_args()
    logconf(args.verbose, args.quiet)
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
        total_bytes, chunks = mcbf.chunked(args.file, bootattrs)
        connection.timeout *= 10
        mcbf.erase_flash(connection, bootattrs.memory_range, bootattrs.erase_size)
        connection.timeout /= 10
        _logger.info(f"Flashing {args.file}")
        flash(
            connection,
            chunks,
            total_bytes,
            bootattrs,
            args.quiet or args.verbose,
        )
        mcbf.self_verify(connection)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(
            "\nFlashing failed:",
            f"{type(exc).__name__}: {exc}" if str(exc) else f"{type(exc).__name__}",
        )
        logging.debug(exc, exc_info=True)


def logconf(verbose: bool, quiet: bool) -> None:
    """Configure log level based on command-line arguments.

    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        return

    if not quiet:
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format="%(message)s",
        )


def flash(
    connection: Serial,
    chunks: Iterator[bincopy.Segment],
    total_bytes: int,
    bootattrs: mcbf.BootAttrs,
    quiet: bool,
) -> None:
    written_bytes = 0
    start = time.time()

    for chunk in chunks:
        mcbf.write_flash(connection, chunk)

        if bootattrs.has_checksum:
            mcbf.checksum(connection, chunk)

        written_bytes += len(chunk.data)
        _logger.debug(
            f"{written_bytes} bytes written of {total_bytes} "
            f"({written_bytes / total_bytes * 100:.2f}%)"
        )

        if not quiet:
            print_progress(written_bytes, total_bytes, time.time() - start)


def print_progress(written_bytes: int, total_bytes: int, elapsed: float) -> None:
    """Print progressbar.

    Parameters
    ----------
    written_bytes : int
        Number of bytes written so far.
    total_bytes : int
        Total number of bytes to write.
    elapsed : float
        Seconds since start.
    """
    ratio = written_bytes / total_bytes
    percentage = f"{100 * ratio:.0f}%"
    print(percentage, end="  ")
    datasize = get_datasize(written_bytes)
    print(datasize, end=" ")
    timer = get_timer(elapsed)
    pbar = get_bar(ratio, len(percentage) + len(datasize) + len(timer))
    print(pbar, end="  ")
    print(timer, end="")
    print(end="\n" if written_bytes == total_bytes else "\r")


def get_datasize(written_bytes: int) -> str:
    """Get human-readable datasize as string.

    Parameters
    ----------
    written_bytes : int
        Number of bytes written so far.

    Returns
    -------
    str
    """
    digits = len(str(written_bytes))

    if digits < 4:
        datasize = f"{written_bytes} B"
    elif digits < 7:
        datasize = f"{written_bytes / 1024:.1f} KiB"
    else:
        datasize = f"{written_bytes / 1024**2:.1f} MiB"

    return datasize


def get_timer(elapsed: float) -> str:
    """Get a timer string formatted as H:MM:SS.

    Parameters
    ----------
    elapsed : float
        Time since start.

    Returns
    -------
    str
    """
    hours, minutes = divmod(elapsed, 3600)
    hours = int(hours)
    minutes, seconds = divmod(minutes, 60)
    minutes = int(minutes)
    seconds = int(seconds)

    return f"Elapsed Time: {hours}:{minutes:02}:{seconds:02}"


def get_bar(done_ratio: float, used_width: int) -> str:
    """Get progressbar string.

    Parameters
    ----------
    done_ratio : float
        A value between zero and one.
    used_width : int
        Number of characters already used by other elements.

    Returns
    -------
    str
    """
    max_width = min(shutil.get_terminal_size().columns, 80)
    bar_width = max_width - used_width - 2
    done = int(bar_width * done_ratio)
    left = bar_width - done
    progressbar = "|" + done * "#" + left * " " + "|"

    return progressbar
