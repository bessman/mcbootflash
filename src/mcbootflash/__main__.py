"""Command line tool for flashing firmware."""

from __future__ import annotations

import argparse
import logging
import shutil
import struct
import sys
import time
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Final, TextIO

import bincopy  # type: ignore[import-untyped]
from serial import Serial, SerialException  # type: ignore[import-untyped]

from mcbootflash import (
    BadAddress,
    BootAttrs,
    BootloaderError,
    Chunk,
    VerifyFail,
    __version__,
    checksum,
    chunked,
    erase_flash,
    get_boot_attrs,
    reset,
    self_verify,
    write_flash,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

if sys.version_info >= (3, 10):
    from itertools import pairwise
else:

    def pairwise(iterable):  # noqa: ANN001, ANN201, D103
        # pairwise('ABCDEFG') → AB BC CD DE EF FG
        iterator = iter(iterable)
        a = next(iterator, None)

        for b in iterator:
            yield a, b
            a = b


logger = logging.getLogger(__name__)
APPNAME: Final[str] = "mcbootflash"


class HandledException(Exception):
    """Raised to signal that an exception has been caught and handled."""


# %%#############
# Input parsing #
#################


def get_parser() -> argparse.ArgumentParser:
    """Parse arguments from command line.

    If `--version` is passed as an argument, print mcbootflash version and exit.

    Returns
    -------
    argparse.Namespace
        The returned ArgumentParser contains the following arguments::

            hexfile: str
            port: str
            baudrate: int
            timeout: float, default=1
            checksum: bool, default=False
            debug: bool, default=False
            quiet: bool,  default=False
    """
    parser = argparse.ArgumentParser(
        prog=APPNAME,
        description=(
            f"{APPNAME} is a tool for flashing firmware to 16-bit Microchip MCUs and "
            "DSCs from the PIC24 and dsPIC33 device families, which are running a "
            "bootloader generated by the MPLAB Code Configurator tool."
        ),
    )
    parser.add_argument(
        "hexfile",
        type=str,
        help="an Intel HEX file containing application firmware",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        required=True,
        help="serial port connected to the device you want to flash",
    )
    parser.add_argument(
        "-b",
        "--baudrate",
        type=baudrate,
        required=True,
        help="symbol rate of device's serial bus",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1,
        help="try to read data from the bus for this many seconds before giving up",
    )
    parser.add_argument(
        "--checksum",
        action="store_true",
        help="verify flashed data by checksumming after write",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="reset device after flashing is complete",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="print debug messages",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{__version__}",
    )
    return parser


def baudrate(baudrate: str) -> int:
    """Sanitize baudrate.

    Parameters
    ----------
    baudrate : str

    Raises
    ------
    argparse.ArgumentTypeError

    Returns
    -------
    int
    """
    if not baudrate.isdecimal():
        msg = f"invalid baudrate value: '{baudrate}'"
        raise argparse.ArgumentTypeError(msg)

    return int(baudrate)


# %%#######
# Logging #
###########


def setup_logging(*, quiet: bool, debug: bool) -> TextIO:
    """Return stream to which to log.

    If both 'quiet' and 'debug' are True, 'debug' takes precedence.

    Parameters
    ----------
    quiet : bool
        If True, only WARNING and above are logged.
    debug : bool
        If True, log messages are written to stdout instead of file.

    Returns
    -------
    TextIO
    """
    logger.setLevel(logging.DEBUG)

    # Log debug messages to stdout if --debug, else to in-memory stream.
    debug_stream = sys.stdout if debug else StringIO()
    handler_debug = logging.StreamHandler(debug_stream)
    handler_debug.setLevel(logging.DEBUG)
    handler_debug.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    # Add debug handler to root logger to receive debug messages from other modules.
    root = logging.getLogger()
    root.addHandler(handler_debug)
    root.setLevel(logging.DEBUG)

    if debug:
        # Info is logged to stdout by debug handler.
        return debug_stream

    if quiet:
        # Don't log info and below to stdout.
        return debug_stream

    # Log info to stdout unless --quiet.
    handler_info = logging.StreamHandler(sys.stdout)
    handler_info.setLevel(logging.INFO)
    logger.addHandler(handler_info)
    return debug_stream


def write_error_log(debug_stream: StringIO | TextIO) -> None:
    """Try to write log.

    Parameters
    ----------
    debug_stream : StringIO | TextIO
    """
    try:
        if debug_stream is sys.stdout:
            logger.debug("Debugging to stdout, skipping log file write")
            return

        assert isinstance(debug_stream, StringIO)

        log_file = Path(f"./{APPNAME}.log")
        with log_file.open("w") as fout:
            fout.write(debug_stream.getvalue())
    except Exception:  # noqa: BLE001
        logger.error("Error: Failed to write log file")
        logger.error(
            "Please re-run app with --debug and save the output manually",
        )
    else:
        logger.error(f"Error log written to {log_file.absolute()}")
    finally:
        # If this is reached, it is a bug in mcbootflash. Even if the user did something
        # wrong, the error should be handled earlier with a better error message.
        logger.error(
            "This should not happen. Please make a bug report at "
            "https://github.com/bessman/mcbootflash/issues",
        )
        logger.error("Include the error log in the report")


# %%########
# Flashing #
############


def connect(port: str, baudrate: int, timeout: float) -> Serial:
    """Try to open serial port.

    Parameters
    ----------
    port : str
    baudrate : int
    timeout : float

    Raises
    ------
    HandledException

    Returns
    -------
    Serial
        Open serial connection.
    """
    try:
        connection = Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
        )
        connection.reset_input_buffer()
    except SerialException as exc:
        raise HandledException("Error: " + str(exc)) from exc

    return connection


def handshake(connection: Serial) -> BootAttrs:
    """Make sure we're actually talking to an MCC bootloader."""
    try:
        try:
            boot_attrs = get_boot_attrs(connection)
        except struct.error as e:
            # Got too few bytes to unpack, i.e. read timeout.
            msg = "Error: Timeout during handshake"
            raise HandledException(msg) from e
        except BootloaderError as e:
            # We read enough bytes, but they weren't what we expected.
            msg = "Error: Bad handshake response"
            raise HandledException(msg) from e
    except HandledException:
        logger.error(f"Error: Could not connect on {connection.name}")
        raise

    return boot_attrs


def parse_hex(hex_file: str, boot_attr: BootAttrs) -> tuple[int, Iterator[Chunk]]:
    """Try to parse the firmware image.

    Parameters
    ----------
    hex_file : str
    boot_attr : BootAttrs

    Raises
    ------
    HandledException

    Returns
    -------
    tuple[int, Iterator[Chunk]]

    """
    try:
        return chunked(hex_file, boot_attr)
    except bincopy.Error as exc:
        raise HandledException("Error: " + str(exc)) from exc


def erase(connection: Serial, erase_range: tuple[int, int], erase_size: int) -> None:
    """Erase flash pages one at a time.

    Parameters
    ----------
    connection : serial.Serial
        Open serial connection to device in bootloader mode.
    erase_range: tuple[int, int]
        Memory range to erase.
    erase_size: int
        Size of a flash page in bytes.
    """
    page_boundaries = range(*erase_range, erase_size)
    total_pages = len(page_boundaries) - 1
    time_start = time.time()

    try:
        for erased_pages, page in enumerate(pairwise(page_boundaries), start=1):
            erase_flash(connection, page, erase_size)
            print_progress(
                erased_pages * erase_size,
                total_pages * erase_size,
                time.time() - time_start,
            )
    except BadAddress:
        # Some bootloader versions incorrectly think addresses greater than
        # 0xFFFF are misaligned.
        logger.debug("Got BAD_ADDRESS during erase")
        logger.debug("This is probably a bug in the bootloader, not mcbootflash")
        logger.debug("Attempting workaround by erasing all remaining pages at once")
        # Erasing many pages at once may take a while.
        tmp_timeout = connection.timeout

        if connection.timeout:
            connection.timeout *= 10

        erase_flash(connection, (page[0] - erase_size, erase_range[1]), erase_size)
        connection.timeout = tmp_timeout
        erased_pages = total_pages
        print_progress(
            erased_pages * erase_size,
            total_pages * erase_size,
            time.time() - time_start,
        )


def flash(
    connection: Serial,
    chunks: Iterator[Chunk],
    total_bytes: int,
    *,
    verify_checksum: bool,
) -> None:
    """Flash application firmware.

    Parameters
    ----------
    connection : serial.Serial
        Open serial connection to device in bootloader mode.
    chunks : Iterator[bincopy.Segment]
        Appropriately sized chunks of data, as generated by `chunked.`.
    total_bytes : int
        Total number of bytes to be written.
    verify_checksum : bool
        Verify integrity of written data.
    """
    written_bytes = 0
    start = time.time()

    for chunk in chunks:
        write_flash(connection, chunk)

        if verify_checksum:
            checksum(connection, chunk)

        written_bytes += len(chunk.data)
        logger.debug(
            f"{written_bytes} bytes written of {total_bytes} "
            f"({written_bytes / total_bytes * 100:.2f}%)",
        )
        print_progress(written_bytes, total_bytes, time.time() - start)


# %%############
# Progress bar #
################


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
    exactly_info = any(h.level == logging.INFO for h in logger.handlers)

    if not exactly_info:
        # Only print progressbar if at least one handler has log level INFO, not higher
        # or lower.
        return

    ratio = written_bytes / total_bytes
    percentage = f"{100 * ratio:.0f}%"
    datasize = get_datasize(written_bytes)
    timer = get_timer(elapsed)
    progress = get_bar(
        ratio,
        len(percentage) + len(datasize) + len(timer) + 3 * len("  "),
    )
    print(  # noqa: T201
        percentage,
        datasize,
        progress,
        timer,
        sep="  ",
        end="\n" if written_bytes == total_bytes else "\r",
    )


def get_datasize(written_bytes: float) -> str:
    """Get human-readable datasize as string.

    Parameters
    ----------
    written_bytes : int
        Number of bytes written so far.

    Returns
    -------
    str
    """
    decimals = 0

    for _prefix in ("", "Ki", "Mi"):
        next_prefix = 1000

        if written_bytes < next_prefix:
            break

        written_bytes /= 1024
        decimals = 1

    return f"{written_bytes:.{decimals}f} {_prefix}B"


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
    return "|" + done * "#" + left * " " + "|"


# %%####
# Main #
########


def main(args: None | argparse.Namespace = None) -> int:
    """Entry point for CLI.

    Paramaters
    ----------
    args: None | argparse.Namespace, default=None
        `main` should normally be called with no arguments, in which case arguments are
        parsed from `sysv`. A pre-parsed argument namespace can be supplied for testing
        purposes.

    Returns
    -------
    return_code: int
        0 if no error occurred, 1 otherwise.
    """
    args = args if args is not None else get_parser().parse_args()
    debug_stream = setup_logging(quiet=args.quiet, debug=args.debug)
    logger.debug(f"{APPNAME} {__version__}")
    logger.debug(vars(args))

    try:
        try:
            logger.info("Connecting to bootloader...")
            connection = connect(args.port, args.baudrate, args.timeout)
            boot_attrs = handshake(connection)
            total_bytes, chunks = parse_hex(args.hexfile, boot_attrs)
            logger.info("Erasing program area...")
            erase(
                connection,
                erase_range=boot_attrs.memory_range,
                erase_size=boot_attrs.erase_size,
            )
            logger.info(f"Flashing {args.hexfile}...")
            flash(
                connection,
                chunks,
                total_bytes=total_bytes,
                verify_checksum=args.checksum,
            )
            self_verify(connection)
            logger.info("Self verify OK")

            if args.reset:
                reset(connection)
        except BaseException:
            # Log all exceptions.
            logger.debug("", exc_info=True)
            raise
        else:
            return 0
    except HandledException as e:
        # The exception has been handled and contains a helpful error message which
        # we want to show to the user.
        logger.error(e)
        return 1
    except KeyboardInterrupt:
        # User said to exit early.
        return 1
    except VerifyFail:
        # This probably means mcbootflash did something wrong while flashing.
        logger.error(
            "Error: Flashing completed but bootloader says application is not bootable",
        )
        write_error_log(debug_stream)
        return 1
    except BaseException:  # noqa: BLE001
        # Unhandled exception, write debug log to file and ask user to report the bug.
        logger.error("Error: An unexpected error occurred")
        write_error_log(debug_stream)
        return 1


if __name__ == "__main__":
    sys.exit(main())
