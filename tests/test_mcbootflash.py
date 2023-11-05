import argparse
import logging
import struct

import bincopy
import pytest
from serial import Serial

import mcbootflash.__main__ as mcmain
import mcbootflash.flash as mcbf
import mcbootflash.protocol

PORTNAME = "/dev/ttyUSB0"
BAUDRATE = 460800


@pytest.fixture
def connection():
    yield Serial(port=PORTNAME, baudrate=BAUDRATE, timeout=1)


def test_wrong_packet():
    resp = mcbootflash.protocol.Checksum(mcbootflash.protocol.CommandCode.CALC_CHECKSUM)
    with pytest.raises(struct.error) as excinfo:
        mcbootflash.protocol.Version.from_bytes(bytes(resp))
    assert "expected 37 bytes, got 14" in str(excinfo)


@pytest.mark.parametrize(
    ["verbose", "quiet"],
    [(False, False), (True, False), (False, True)],
)
def test_cli(reserial, caplog, verbose, quiet):
    caplog.set_level(logging.INFO)
    mcmain.main(
        argparse.Namespace(
            **{
                "file": "tests/testcases/flash/test.hex",
                "port": PORTNAME,
                "baudrate": BAUDRATE,
                "timeout": 1,
                "verbose": verbose,
                "quiet": quiet,
            }
        )
    )
    assert "Self verify OK" in caplog.messages[-1]


def test_cli_no_response(reserial, capsys):
    mcmain.main(
        argparse.Namespace(
            **{
                "file": "tests/testcases/flash/test.hex",
                "port": PORTNAME,
                "baudrate": BAUDRATE,
                "timeout": 1,
                "verbose": True,
                "quiet": False,
            }
        )
    )
    assert "Flashing failed" in capsys.readouterr().out


def test_get_parser():
    parser = mcmain.get_parser()
    assert parser.description == (
        "Flash firmware over serial connection to a device "
        "running Microchip's 16-bit bootloader."
    )


def test_datasize_large():
    assert mcmain.get_datasize(1e6) == "1.0 MiB"


def test_progressbar(capsys):
    mcmain.print_progress(100, 200, 5)
    expected = (
        "50%  100 B |########################                         |  "
        "Elapsed Time: 0:00:05\r"
    )
    assert capsys.readouterr().out == expected


def test_get_bootattrs(reserial, connection):
    assert mcbf.get_boot_attrs(connection) == mcbf.BootAttrs(
        version=258,
        max_packet_length=256,
        device_id=13398,
        erase_size=2048,
        write_size=8,
        memory_range=(6144, 174080),
        has_checksum=True,
    )


def test_erase(reserial, caplog, connection):
    # To record data for this test, connect a device with an application installed.
    caplog.set_level(logging.INFO)
    bootattrs = mcbf.get_boot_attrs(connection)
    connection.timeout = 10
    mcbf.erase_flash(connection, bootattrs.memory_range, bootattrs.erase_size)
    assert "No application detected; flash erase successful" in caplog.messages[-1]


def test_erase_empty(reserial, caplog, connection):
    # To record data for this test, connect a device with no application installed.
    caplog.set_level(logging.INFO)
    bootattrs = mcbf.get_boot_attrs(connection)
    mcbf.erase_flash(connection, bootattrs.memory_range, bootattrs.erase_size)
    assert "No application detected, skipping flash erase" in caplog.messages[-1]


def test_erase_fail(reserial, connection):
    # To record data for this test, connect a device with an application installed.
    bootattrs = mcbf.get_boot_attrs(connection)
    mcbf._FLASH_UNLOCK_KEY = 0
    with pytest.raises(mcbf.BootloaderError) as excinfo:
        mcbf.erase_flash(
            connection,
            bootattrs.memory_range,
            bootattrs.erase_size,
        )
    assert "could not be erased" in str(excinfo.value)


def test_erase_misaligned():
    with pytest.raises(ValueError) as excinfo:
        mcbf.erase_flash(Serial(), (0, 1), 2)
    assert "not a multiple" in str(excinfo.value)


def test_checksum_error(reserial, connection):
    bootattrs = mcbf.get_boot_attrs(connection)
    chunk = bincopy.Segment(
        minimum_address=bootattrs.memory_range[0],
        maximum_address=bootattrs.memory_range[0] + bootattrs.write_size,
        data=bytes(bootattrs.write_size),
        word_size_bytes=1,
    )
    with pytest.raises(mcbf.BootloaderError) as excinfo:
        mcbf.checksum(connection, chunk)
    assert "Checksum mismatch" in str(excinfo.value)


def test_checksum_not_supported(reserial, caplog, connection):
    mcbf.get_boot_attrs(connection)
    assert "Bootloader does not support checksumming" in caplog.messages


def test_no_data():
    bootattrs = mcbf.BootAttrs(
        version=258,
        max_packet_length=256,
        device_id=13398,
        erase_size=2048,
        write_size=8,
        memory_range=(6144, 174080),
        has_checksum=True,
    )
    with pytest.raises(ValueError) as excinfo:
        mcbf.chunked("tests/testcases/no_data/test.hex", bootattrs)
    assert "no data" in str(excinfo.value)


def test_reset(reserial, caplog, connection):
    caplog.set_level(logging.INFO)
    mcbf.reset(connection)
    assert "Device reset" in caplog.messages[-1]


def test_unexpected_response(reserial, connection):
    with pytest.raises(mcbf.BootloaderError) as excinfo:
        mcbf.reset(connection)
    assert "Command code mismatch" in str(excinfo.value)


def test_read_flash():
    with pytest.raises(NotImplementedError):
        mcbf._read_flash(Serial())
