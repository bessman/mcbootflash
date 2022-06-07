import shlex

import pytest
import pytest_mock

from mcbootflash.flash import flash


@pytest.mark.parametrize("options", ("--help",))
def test_help(capsys, options):
    try:
        flash([options])
    except SystemExit:
        pass
    output = capsys.readouterr().out
    assert "Flash firmware over serial connection" in output


@pytest.mark.parametrize(
    "options",
    ("test/test.hex --port mock_serial.port --baudrate 460800",),
)
def test_flash(options, mocker):
    mocker.patch("mcbootflash.flash.BootloaderConnection")
    for i in range(5):
        flash(shlex.split(options) + ["-" * (i > 0) + "v" * i] * (i > 0))
