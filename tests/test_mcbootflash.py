import argparse
import logging
import struct

import bincopy
import pytest
from serial import Serial

import mcbootflash as mcbf
from mcbootflash.__main__ import _checksum, _chunk, _flash, main

PORTNAME = "/dev/ttyUSB0"


@pytest.fixture
def connection():
    yield Serial(port=PORTNAME, baudrate=460800, timeout=5)


@pytest.mark.parametrize(
    ["verbose", "quiet"],
    [(False, False), (True, False), (False, True)],
)
def test_cli(reserial, verbose, quiet, caplog):
    caplog.set_level(logging.INFO)
    main(
        argparse.Namespace(
            **{
                "file": "tests/testcases/flash/test.hex",
                "port": PORTNAME,
                "baudrate": 460800,
                "timeout": 1,
                "verbose": verbose,
                "quiet": quiet,
            }
        )
    )
    assert "Self verify OK" in caplog.messages[-1]


def test_erase(reserial, caplog, connection):
    caplog.set_level(logging.INFO)
    mcbf.erase_flash(connection, (0, 0), 1, force=True)
    assert "No application detected; flash erase successful" in caplog.messages[-1]


def test_erase_empty(reserial, caplog, connection):
    caplog.set_level(logging.INFO)
    mcbf.erase_flash(connection, (0, 0), 1)
    assert "No application detected, skipping flash erase" in caplog.messages[-1]


def test_erase_fail(reserial, connection):
    with pytest.raises(mcbf.BootloaderError) as excinfo:
        mcbf.erase_flash(connection, (0, 0), 1)
    assert "could not be erased" in str(excinfo.value)


def test_erase_misaligned(connection):
    with pytest.raises(ValueError) as excinfo:
        mcbf.erase_flash(connection, (0, 1), 2)
    assert "not a multiple" in str(excinfo.value)


def test_checksum_error(reserial, connection):
    chunk = bincopy.Segment()
    with pytest.raises(mcbf.BootloaderError) as excinfo:
        mcbf.checksum(connection, chunk)
    assert "Checksum mismatch" in str(excinfo.value)


def test_no_data():
    bootattrs = mcbf.BootAttrs()
    with pytest.raises(mcbf.BootloaderError) as excinfo:
        _chunk("tests/testcases/no_data/test.hex", bootattrs)
    assert "no data" in str(excinfo.value)


def test_reset(reserial, caplog, connection):
    caplog.set_level(logging.INFO)
    mcbf.reset(connection)
    assert "Device reset" in caplog.messages[-1]


def test_unexpected_response(reserial, connection):
    with pytest.raises(mcbf.BootloaderError) as excinfo:
        mcbf.reset(connection)
    assert "Command code mismatch" in str(excinfo.value)


def test_read_flash(reserial):
    connection = Serial(port=PORTNAME, baudrate=460800)
    with pytest.raises(NotImplementedError):
        mcbf._read_flash(connection)


def test_checksum_workaround(caplog, connection):
    caplog.set_level(logging.DEBUG)
    chunk = bincopy.Segment()
    bootattrs = mcbf.BootAttrs()
    _checksum(connection, chunk, bootattrs)
    # There's some other stuff after the message we're interested in.
    assert "skipping checksum calculation" in caplog.messages[-5]


def test_checksum_not_supported(reserial, caplog, connection):
    chunk = bincopy.Segment()
    bootattrs = mcbf.BootAttrs()
    _flash(connection, [chunk], 0, bootattrs)
    assert "Bootloader does not support checksums" in caplog.messages
