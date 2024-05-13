import argparse
import logging
import struct
from pathlib import Path

import bincopy
import pytest
from serial import Serial

import mcbootflash as bf
import mcbootflash.__main__ as main
import mcbootflash.flash
import mcbootflash.types

PORTNAME = "/dev/ttyUSB0"
BAUDRATE = 460800


@pytest.fixture()
def connection():
    return Serial(port=PORTNAME, baudrate=BAUDRATE, timeout=1)


def test_wrong_packet():
    resp = mcbootflash.types.Checksum(mcbootflash.types.CommandCode.CALC_CHECKSUM)
    with pytest.raises(struct.error) as excinfo:
        mcbootflash.types.Version.from_bytes(bytes(resp))
    assert "expected 37 bytes, got 14" in str(excinfo)


@pytest.mark.parametrize(
    ("verbose", "quiet"),
    [(False, False), (True, False), (False, True)],
)
def test_cli(reserial, caplog, verbose, quiet):
    caplog.set_level(logging.INFO)
    main.main(
        argparse.Namespace(
            hexfile="tests/testcases/flash/test.hex",
            port=PORTNAME,
            baudrate=BAUDRATE,
            timeout=10,
            checksum=True,
            reset=False,
            verbose=verbose,
            quiet=quiet,
        ),
    )
    assert "Self verify OK" in caplog.messages[-1]


def test_cli_error(caplog):
    if Path(PORTNAME).exists():
        msg = f"{PORTNAME} exists: skipping device not connected test"
        pytest.skip(msg)

    caplog.set_level(logging.INFO)
    main.main(
        argparse.Namespace(
            hexfile="tests/testcases/flash/test.hex",
            port=PORTNAME,
            baudrate=BAUDRATE,
            timeout=10,
            checksum=True,
            reset=False,
            verbose=True,
            quiet=False,
        ),
    )
    assert caplog.records[-1].levelno == logging.ERROR


def test_get_parser():
    parser = main.get_parser()
    assert parser.description == (
        "Flash firmware over serial connection to a device "
        "running Microchip's 16-bit bootloader."
    )


def test_datasize_large():
    assert main.get_datasize(2**20) == "1.0 MiB"


def test_progressbar(capsys):
    main.print_progress(100, 200, 5)
    expected = (
        "50%  100 B  |#####################                      |  "
        "Elapsed Time: 0:00:05\r"
    )
    assert capsys.readouterr().out == expected


def test_get_bootattrs(reserial, connection):
    assert bf.get_boot_attrs(connection) == bf.BootAttrs(
        version=258,
        max_packet_length=256,
        device_id=13398,
        erase_size=2048,
        write_size=8,
        memory_range=(6144, 174080),
    )


def test_erase(reserial, caplog, connection):
    caplog.set_level(logging.DEBUG)
    bootattrs = bf.get_boot_attrs(connection)
    connection.timeout = 10
    bf.erase_flash(connection, bootattrs.memory_range, bootattrs.erase_size)
    assert "Erasing addresses" in caplog.messages[-4]


def test_erase_misaligned():
    with pytest.raises(ValueError) as excinfo:
        bf.erase_flash(Serial(), (0, 1), 2)
    assert "not a multiple" in str(excinfo.value)


def test_checksum_error(reserial, connection):
    bootattrs = bf.get_boot_attrs(connection)
    chunk = bincopy.Segment(
        minimum_address=bootattrs.memory_range[0],
        maximum_address=bootattrs.memory_range[0] + bootattrs.write_size,
        data=bytes(bootattrs.write_size),
        word_size_bytes=1,
    )
    with pytest.raises(bf.BootloaderError) as excinfo:
        bf.checksum(connection, chunk)
    assert "Checksum mismatch" in str(excinfo.value)


def test_no_data():
    bootattrs = bf.BootAttrs(
        version=258,
        max_packet_length=256,
        device_id=13398,
        erase_size=2048,
        write_size=8,
        memory_range=(6144, 174080),
    )
    with pytest.raises(ValueError) as excinfo:
        bf.chunked("tests/testcases/no_data/test.hex", bootattrs)
    assert "no data" in str(excinfo.value)


def test_reset(reserial, caplog, connection):
    caplog.set_level(logging.DEBUG)
    bf.reset(connection)
    assert "Device reset" in caplog.messages[-1]


def test_unexpected_response(reserial, connection):
    with pytest.raises(bf.BootloaderError) as excinfo:
        bf.reset(connection)
    assert "Command code mismatch" in str(excinfo.value)


def test_verify_fail(reserial, connection):
    with pytest.raises(bf.VerifyFail):
        bf.self_verify(connection)


def test_read_flash():
    with pytest.raises(NotImplementedError):
        mcbootflash.flash._read_flash()


def test_format_debug_bytes():
    testbytes_tx = b"0123"
    testbytes_rx = b"456789"
    formatted_tx = mcbootflash.flash._format_debug_bytes(testbytes_tx)
    formatted_rx = mcbootflash.flash._format_debug_bytes(testbytes_rx, testbytes_tx)
    expected = "30 31 32 33\n            34 35 36 37 38 39"
    assert formatted_tx + "\n" + formatted_rx == expected


def test_checksum_bad_address_warning(reserial, caplog, connection):
    boot_attrs = bf.get_boot_attrs(connection)
    payload_size = 240
    chunk = bincopy.Segment(
        minimum_address=boot_attrs.memory_range[1] - payload_size // 2,
        maximum_address=boot_attrs.memory_range[1],
        data=b"\xff" * payload_size,
        word_size_bytes=1,
    )
    bf.checksum(connection, chunk)
    assert "BadAddress" in caplog.messages[-1]
