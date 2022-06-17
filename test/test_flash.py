import argparse

import pytest
import pytest_mock

from mcbootflash.flash import get_parser, flash


def test_overwrite_cli_arg():
    parser = get_parser()
    try:
        parser.add_argument("-b", "--baudrate", default=460800)
    except argparse.ArgumentError:  # pragma: no cover
        pytest.fail()


test_namespace = argparse.Namespace(
    **{
        "file": "test/test.hex",
        "port": "mockport",
        "baudrate": 460800,
        "timeout": 5,
        "verbose": False,
        "quiet": False,
    }
)


def test_flash(mocker):
    mocker.patch("mcbootflash.flash.BootloaderConnection")
    flash(test_namespace)


def test_flash_quiet(mocker):
    mocker.patch("mcbootflash.flash.BootloaderConnection")
    test_namespace.quiet = True
    flash(test_namespace)


def test_flash_verbose(mocker):
    mocker.patch("mcbootflash.flash.BootloaderConnection")
    test_namespace.verbose = True
    flash(test_namespace)
