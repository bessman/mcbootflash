"""Command line tool for flashing firmware."""
import argparse
import logging
from typing import Union

try:
    import progressbar  # type: ignore[import]

    _PROGRESSBAR_AVAILABLE = True
except ImportError:
    _PROGRESSBAR_AVAILABLE = False

from mcbootflash.connection import Bootloader, ProgressCallback
from mcbootflash.error import BootloaderError

_logger = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    """Return a populated ArgumentParser instance.

    This function is meant to be used by applications which want to create their own CLI
    while using mcbootflash in the background.

    Returns
    -------
    argparse.ArgumentParser
        The returned ArgumentParser has the following arguments already added::

            file           (str,   required)
            -p, --port     (str,   required)
            -b, --baudrate (int,   required)
            -t, --timeout  (float, default=5)
            -v, --verbose  (bool,  default=False)
            -q, --quiet    (bool,  default=False)

        These arguments can be overridden by adding a new argument with the same option
        string. For example, an application which only needs to communicate with a
        specific device with a known serial baudrate could override the 'baudrate'
        option to make it optional::

            import mcbootflash
            parser = mcbootflash.get_parser()
            parser.add_argument("-b", "--baudrate", default=460800)
            mcbootflash.flash(parser.parse_args())
    """
    parser = argparse.ArgumentParser(
        description=(
            "Flash firmware over serial connection to a device running Microchip's "
            "16-bit bootloader."
        ),
        conflict_handler="resolve",
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

    return parser


class _Bar:
    pbar = None

    @staticmethod
    def callback(written_bytes: int, total_bytes: int) -> None:
        if not _Bar.pbar:
            widgets = [
                progressbar.Percentage(),
                " ",
                progressbar.DataSize(),
                " ",
                progressbar.Bar(),
                " ",
                progressbar.Timer(),
            ]
            progress = progressbar.ProgressBar(widgets=widgets)
            _Bar.pbar = progress.start(max_value=total_bytes)

        if written_bytes == total_bytes:
            assert isinstance(_Bar.pbar, progressbar.ProgressBar)
            _Bar.pbar.finish()
            _Bar.pbar = None
        else:
            assert isinstance(_Bar.pbar, progressbar.ProgressBar)
            _Bar.pbar.update(value=written_bytes)

    @staticmethod
    def fallback(written_bytes: int, total_bytes: int) -> None:
        print(f"{100 * written_bytes/total_bytes:.0f}%", end=" ")
        print(f"Wrote {written_bytes}/{total_bytes} bytes.", end=" ")
        print(end="\n" if written_bytes == total_bytes else "\r")


def flash(parsed_args: Union[None, argparse.Namespace] = None) -> None:
    """Command line script for firmware flashing.

    Use this directly or indirectly as entry point for project.scripts.

    Parameters
    ----------
    parsed_args : argparse.Namespace, optional
        Pre-parsed arguments. If not specified, arguments will be parsed from the
        command line.
    """
    parsed_args = parsed_args or get_parser().parse_args()
    callback = _logconf(parsed_args)

    try:
        boot = Bootloader(
            port=parsed_args.port,
            baudrate=parsed_args.baudrate,
            timeout=parsed_args.timeout,
        )
        boot.flash(
            hexfile=parsed_args.file,
            progress_callback=callback,
        )
    except BootloaderError as exc:
        print(
            "\nFlashing failed:",
            f"{type(exc).__name__}: {exc}" if str(exc) else f"{type(exc).__name__}",
        )
        logging.debug(exc, exc_info=True)


def _logconf(parsed_args: argparse.Namespace) -> Union[ProgressCallback, None]:
    callback = None

    if not parsed_args.quiet:
        if _PROGRESSBAR_AVAILABLE:
            callback = _Bar.callback
            progressbar.streams.wrap_stderr()
        else:
            _logger.warning("'progressbar' package not available. Using fallback.")
            callback = _Bar.fallback

        logging.basicConfig(
            level=logging.DEBUG if parsed_args.verbose else logging.INFO,
            format="%(message)s",
        )

    if parsed_args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    return callback
