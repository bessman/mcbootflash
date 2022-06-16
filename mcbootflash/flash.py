"""Command line tool for flashing firmware."""

import argparse
import logging
from typing import Union

import progressbar

from mcbootflash import BootloaderConnection


def get_parser() -> argparse.ArgumentParser:
    """Return a populated ArgumentParser instance.

    This function is meant to be used by applications which want to create their own CLI
    while using mcbootflash in the background.

    The returned ArgumentParser has the following arguments already added:
        file           (str,   required)
        -p, --port     (str,   required)
        -b, --baudrate (int,   required)
        -t, --timeout  (float, default=5)
        -v, --verbose  (bool,  default=False)
        -q, --quiet    (bool,  default=False)

    These arguments can be overridden by adding a new argument with the same name. For
    example, an application which only needs to communicate with a specific device with
    a known serial baudrate could override the 'baudrate' option to make it optional:

        from mcbootflash.flash import flash, get_parser
        parser = get_parser()
        parser.add_argument("--baudrate", default=460800)
        flash(parser.parse_args())
    """
    parser = argparse.ArgumentParser(
        prog="mcbootflash",
        usage=(
            "Flash firmware over serial connection to a device running Microchip's "
            "16-bit bootloader."
        ),
        conflict_handler="resolve",
    )
    parser.add_argument(
        "file",
        type=str,
        required=True,
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
    return parser


def flash(parsed_args: Union[None, argparse.Namespace] = None) -> None:
    """Entry point for console_script."""
    parsed_args = parsed_args or get_parser().parse_args()
    progressbar.streams.wrap_stderr()

    if parsed_args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif not parsed_args.quiet:
        logging.basicConfig(level=logging.INFO, format="%(levelname)5s: %(message)s")
    else:
        logging.basicConfig(level=logging.ERROR)

    boot = BootloaderConnection(
        port=parsed_args.port,
        baudrate=parsed_args.baudrate,
        timeout=parsed_args.timeout,
        quiet=parsed_args.quiet,
    )
    boot.flash(hexfile=parsed_args.file)
    boot.close()
