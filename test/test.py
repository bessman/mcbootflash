import argparse

import pytest

from mcbootflash import (
    BootloaderConnection,
    ChecksumError,
    ConnectionFailure,
    FlashEraseFail,
    NoData,
    UnexpectedResponse,
    flash,
    get_parser,
)


@pytest.mark.parametrize(
    ["verbose", "quiet"],
    [(False, False), (True, False), (False, True)],
)
@pytest.mark.parametrize("device", ["test/testcases/flash/traffic.json"], indirect=True)
def test_flash(device, verbose, quiet):
    flash(
        argparse.Namespace(
            **{
                "file": "test/testcases/flash/test.hex",
                "port": device.port,
                "baudrate": 460800,
                "timeout": 1,
                "verbose": verbose,
                "quiet": quiet,
            }
        )
    )
    assert all(device.stubs[i].called for i in device.stubs)


def test_overwrite_args(capsys):
    parser = get_parser()
    parser.add_argument("-b", "--baudrate", default=460800, help=argparse.SUPPRESS)
    parser.print_help()
    assert "baudrate" not in capsys.readouterr().out


@pytest.mark.parametrize("device", ["test/testcases/erase/traffic.json"], indirect=True)
def test_erase(device):
    blc = BootloaderConnection(port=device.port, timeout=1)
    blc.erase_flash(force=True)
    assert all(device.stubs[i].called for i in device.stubs)


@pytest.mark.parametrize(
    "device",
    ["test/testcases/erase_empty/traffic.json"],
    indirect=True,
)
def test_erase_empty(device):
    blc = BootloaderConnection(port=device.port, timeout=1)
    blc.erase_flash()
    assert all(device.stubs[i].called for i in device.stubs)


@pytest.mark.parametrize(
    "device",
    ["test/testcases/erase_fail/traffic.json"],
    indirect=True,
)
def test_erase_fail(device):
    blc = BootloaderConnection(port=device.port, timeout=1)
    blc._FLASH_UNLOCK_KEY = 0
    with pytest.raises(FlashEraseFail):
        blc.erase_flash()


@pytest.mark.parametrize(
    "device",
    ["test/testcases/flash_empty/traffic.json"],
    indirect=True,
)
def test_flash_empty(device):
    blc = BootloaderConnection(port=device.port, timeout=1)
    blc.flash("test/testcases/flash_empty/test.hex")
    assert all(device.stubs[i].called for i in device.stubs)


@pytest.mark.parametrize(
    "device",
    ["test/testcases/checksum_error/traffic.json"],
    indirect=True,
)
def test_checksum_error(device):
    blc = BootloaderConnection(port=device.port, timeout=1)
    blc._FLASH_UNLOCK_KEY = 0
    with pytest.raises(ChecksumError):
        blc.flash("test/testcases/checksum_error/test.hex")


@pytest.mark.parametrize(
    "device",
    ["test/testcases/no_data/traffic.json"],
    indirect=True,
)
def test_no_data(device):
    blc = BootloaderConnection(port=device.port, timeout=1)
    with pytest.raises(NoData):
        blc.flash("test/testcases/no_data/test.hex")


@pytest.mark.parametrize("device", ["test/testcases/reset/traffic.json"], indirect=True)
def test_reset(device):
    blc = BootloaderConnection(port=device.port, timeout=1)
    blc.reset()
    assert all(device.stubs[i].called for i in device.stubs)


@pytest.mark.parametrize(
    "device",
    ["test/testcases/unexpected_response/traffic.json"],
    indirect=True,
)
def test_unexpected_response(device):
    blc = BootloaderConnection(port=device.port, timeout=1)
    with pytest.raises(UnexpectedResponse):
        blc.reset()


def test_read_flash():
    blc = BootloaderConnection()
    with pytest.raises(NotImplementedError):
        blc._read_flash()


@pytest.mark.parametrize(
    "device",
    ["test/testcases/no_response/traffic.json"],
    indirect=True,
)
def test_no_response_from_bootloader(device, capsys):
    flash(
        argparse.Namespace(
            **{
                "file": "test/testcases/no_response/test.hex",
                "port": device.port,
                "baudrate": 460800,
                "timeout": 0.1,
                "verbose": False,
                "quiet": False,
            }
        )
    )
    captured = capsys.readouterr()
    assert "ConnectionFailure" in captured.out
