"""Command line tool for flashing firmware."""

import argparse
import logging

from mcbootflash import BootloaderConnection


def flash(args=None):
    """Entry point for console_script."""
    parser = argparse.ArgumentParser(
        prog="mcbootflash",
        usage=(
            "Flash firmware over serial connection to a device running "
            "Microchip's 16-bit bootloader."
        ),
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
        help=(
            "Try to read data from the serial port for this many seconds "
            "before giving up."
        ),
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)
    args = parser.parse_args(args)
    logging.basicConfig()

    if not args.verbose:
        logging.getLogger().setLevel(logging.CRITICAL)
    elif args.verbose == 1:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose == 2:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.verbose == 3:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.DEBUG)

    boot = BootloaderConnection(
        port=args.port, baudrate=args.baudrate, timeout=args.timeout
    )
    boot.flash(hexfile=args.file)
    boot.close()


if __name__ == "__main__":
    flash()
