import argparse
import logging

import pytest

from mcbootflash import Bootloader, BootloaderError, __version__, flash, get_parser
from mcbootflash.__main__ import main

PORTNAME = "/dev/ttyUSB0"


@pytest.mark.parametrize(
    ["verbose", "quiet"],
    [(False, False), (True, False), (False, True)],
)
def test_flash(reserial, verbose, quiet, caplog):
    caplog.set_level(logging.INFO)
    flash(
        argparse.Namespace(
            **{
                "file": "tests/testcases/flash/test.hex",
                "port": PORTNAME,
                "baudrate": 460800,
                "timeout": 5,
                "verbose": verbose,
                "quiet": quiet,
            }
        )
    )
    assert "Self verify OK" in caplog.messages[-1]


def test_version(capsys):
    try:
        main(["--version"])
    except SystemExit:
        assert capsys.readouterr().out == f"{__version__}\n"


def test_overwrite_args(capsys):
    parser = get_parser()
    parser.add_argument("-b", "--baudrate", default=460800, help=argparse.SUPPRESS)
    parser.print_help()
    assert "baudrate" not in capsys.readouterr().out


def test_erase(reserial, caplog):
    caplog.set_level(logging.INFO)
    boot = Bootloader(port=PORTNAME, baudrate=460800, timeout=5)
    boot.erase_flash(force=True)
    assert "No application detected; flash erase successful" in caplog.messages[-1]


def test_erase_empty(reserial, caplog):
    caplog.set_level(logging.INFO)
    boot = Bootloader(port=PORTNAME, baudrate=460800, timeout=5)
    boot.erase_flash()
    assert "No application detected, skipping flash erase" in caplog.messages[-1]


def test_erase_fail(reserial):
    boot = Bootloader(port=PORTNAME, baudrate=460800, timeout=5)
    boot._FLASH_UNLOCK_KEY = 0
    with pytest.raises(BootloaderError) as excinfo:
        boot.erase_flash()
    assert "could not be erased" in str(excinfo.value)


def test_flash_empty(reserial, caplog):
    caplog.set_level(logging.INFO)
    boot = Bootloader(port=PORTNAME, baudrate=460800, timeout=5)
    boot.flash("tests/testcases/flash_empty/test.hex")
    assert "Self verify OK" in caplog.messages[-1]


def test_checksum_error(reserial):
    boot = Bootloader(port=PORTNAME, baudrate=460800, timeout=5)
    boot._FLASH_UNLOCK_KEY = 0
    with pytest.raises(BootloaderError) as excinfo:
        boot.flash("tests/testcases/checksum_error/test.hex")
    assert "Checksum mismatch" in str(excinfo.value)


def test_no_data(reserial):
    boot = Bootloader(port=PORTNAME, baudrate=460800, timeout=1)
    with pytest.raises(BootloaderError) as excinfo:
        boot.flash("tests/testcases/no_data/test.hex")
    assert "no data" in str(excinfo.value)


def test_reset(reserial, caplog):
    caplog.set_level(logging.INFO)
    boot = Bootloader(port=PORTNAME, baudrate=460800, timeout=1)
    boot.reset()
    assert "Device reset" in caplog.messages[-1]


def test_unexpected_response(reserial):
    boot = Bootloader(port=PORTNAME, baudrate=460800, timeout=1)
    with pytest.raises(BootloaderError) as excinfo:
        boot.reset()
    assert "Command code mismatch" in str(excinfo.value)


def test_read_flash(reserial):
    boot = Bootloader(port=PORTNAME, baudrate=460800, timeout=1)
    with pytest.raises(NotImplementedError):
        boot._read_flash()


def test_no_response_from_bootloader(reserial, capsys):
    flash(
        argparse.Namespace(
            **{
                "file": "tests/testcases/no_response/test.hex",
                "port": PORTNAME,
                "baudrate": 460800,
                "timeout": 1,
                "verbose": False,
                "quiet": False,
            }
        )
    )
    assert "No response from bootloader" in capsys.readouterr().out


def test_checksum_workaround(reserial, caplog):
    caplog.set_level(logging.DEBUG)
    boot = Bootloader(port=PORTNAME, baudrate=460800, timeout=1)
    boot.flash("tests/testcases/flash/test.hex")
    # Final log message is 'Self verify OK', we want the one before that.
    assert "skipping checksum calculation" in caplog.messages[-2]
