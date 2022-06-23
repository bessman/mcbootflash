import intelhex
import mock_serial
import pytest
import pytest_mock

from mcbootflash import (
    FLASH_UNLOCK_KEY,
    BadAddress,
    BadLength,
    BootCommand,
    BootloaderConnection,
    BootloaderError,
    BootResponse,
    ChecksumError,
    ChecksumPacket,
    CommandPacket,
    McbootflashException,
    MemoryRangePacket,
    ResponsePacket,
    UnsupportedCommand,
    VerifyFail,
    VersionResponsePacket,
)


@pytest.fixture
def mock_boot(mock_serial):
    boot = BootloaderConnection(port=mock_serial.port, timeout=0.1)
    yield boot
    boot.close()


HEXFILE = intelhex.IntelHex("test/test.hex")


READ_VERSION_RETVALS = {
    "version": 0x0102,
    "max_packet_length": 0x0013,
    "device_id": 0x3456,
    "erase_size": 0x0020,
    "write_size": 0x08,
}


def test_read_version(mock_boot, mock_serial):
    mock_serial.stub(
        receive_bytes=bytes(CommandPacket(command=BootCommand.READ_VERSION)),
        send_bytes=bytes(
            VersionResponsePacket(
                command=BootCommand.READ_VERSION, **READ_VERSION_RETVALS
            )
        ),
    )
    assert mock_boot.read_version() == tuple(READ_VERSION_RETVALS.values())


def mock_read_version(*args, **kwargs):
    return list(READ_VERSION_RETVALS.values())


GET_MEMORY_ADDRESS_RANGE_RETVALS = {
    "program_start": HEXFILE.segments()[0][0] // 2,
    "program_end": HEXFILE.segments()[0][1] // 2,
}


def test_get_memory_address_range(mock_boot, mock_serial):
    retvals = {"program_start": 0x2000, "program_end": 0x4000}
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(command=BootCommand.GET_MEMORY_ADDRESS_RANGE)
        ),
        send_bytes=bytes(
            MemoryRangePacket(
                command=BootCommand.GET_MEMORY_ADDRESS_RANGE,
                success=BootResponse.SUCCESS.value,
                **retvals,
            )
        ),
    )
    assert mock_boot._get_memory_address_range() == tuple(retvals.values())


def mock_get_memory_address_range(*args, **kwargs):
    return list(GET_MEMORY_ADDRESS_RANGE_RETVALS.values())


def test_erase_flash(mock_boot, mock_serial):
    start_address = 0x2000
    end_address = 0x4000
    erase_size = 0x0800
    params = {
        "data_length": int((end_address - start_address) // erase_size),
        "unlock_sequence": FLASH_UNLOCK_KEY,
        "address": start_address,
    }
    mock_serial.stub(
        receive_bytes=bytes(CommandPacket(command=BootCommand.ERASE_FLASH, **params)),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.ERASE_FLASH,
                **params,
                success=BootResponse.SUCCESS,
            )
        ),
    )
    # BootloaderConnection._erase_flash returns nothing and all side effects
    # are bootloader-side. The only thing we can test is that no unexpected
    # exception occurs, hence no assert.
    mock_boot._erase_flash(start_address, end_address, erase_size)


def test_write_flash(mock_boot, mock_serial):
    address = 0x2000
    data = bytes(range(8))
    params = {
        "data_length": len(data),
        "unlock_sequence": FLASH_UNLOCK_KEY,
        "address": address,
    }
    mock_serial.stub(
        receive_bytes=bytes(CommandPacket(command=BootCommand.WRITE_FLASH, **params)),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.WRITE_FLASH,
                **params,
                success=BootResponse.SUCCESS,
            )
        ),
    )
    mock_boot._write_flash(address, data)


def test_self_verify(mock_boot, mock_serial):
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.SELF_VERIFY,
            )
        ),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.SELF_VERIFY,
                success=BootResponse.SUCCESS,
            )
        ),
    )
    mock_boot._self_verify()


EXPECTED_CHECKSUM = 0x10B5


def test_get_checksum(mock_boot, mock_serial):
    address = 0x2000
    length = 0x08
    params = {"data_length": length, "address": address}
    mock_serial.stub(
        receive_bytes=bytes(CommandPacket(command=BootCommand.CALC_CHECKSUM, **params)),
        send_bytes=bytes(
            ChecksumPacket(
                command=BootCommand.CALC_CHECKSUM,
                **params,
                success=BootResponse.SUCCESS,
                checksum=EXPECTED_CHECKSUM,
            )
        ),
    )
    assert mock_boot._get_checksum(address, length) == EXPECTED_CHECKSUM


def mock_get_checksum(*args):
    return EXPECTED_CHECKSUM


def mock_get_incorrect_checksum(*args):
    return 0


def test_calculate_checksum(mock_boot):
    mock_boot.hexfile = intelhex.IntelHex("test/test.hex")
    segments = mock_boot.hexfile.segments()
    address = segments[0][0]
    length = segments[0][1] - segments[0][0]
    assert mock_boot._calculate_checksum(address, length) == EXPECTED_CHECKSUM


def mock_calculate_checksum(*args):
    return EXPECTED_CHECKSUM


def test_checksum(mock_boot, mocker):
    address = 0x2000
    length = 0x08
    mocker.patch.object(
        mock_boot,
        "_get_checksum",
        mock_get_checksum,
    )
    mocker.patch.object(
        BootloaderConnection,
        "_calculate_checksum",
        mock_calculate_checksum,
    )
    mock_boot._checksum(address // 2, length)


def test_checksum_fail(mock_boot, mocker):
    address = 0x2000
    length = 0x08
    mocker.patch.object(
        BootloaderConnection,
        "_get_checksum",
        mock_get_incorrect_checksum,
    )
    mocker.patch.object(
        BootloaderConnection,
        "_calculate_checksum",
        mock_calculate_checksum,
    )
    with pytest.raises(ChecksumError):
        mock_boot._checksum(address // 2, length)


def test_flash_segment(mock_boot, mocker):
    mock_boot.hexfile = HEXFILE
    max_packet_length = 0x13
    write_size = 8
    mocker.patch.object(BootloaderConnection, "_write_flash")
    mocker.patch.object(BootloaderConnection, "_checksum")
    mock_boot._flash_segment(
        mock_boot.hexfile.segments()[0], max_packet_length, write_size
    )
    mock_boot._checksum.assert_called()


def test_flash(mock_boot, mocker):
    mocker.patch.object(
        BootloaderConnection,
        "read_version",
        mock_read_version,
    )
    mocker.patch.object(
        BootloaderConnection,
        "_get_memory_address_range",
        mock_get_memory_address_range,
    )
    mocker.patch.object(BootloaderConnection, "_erase_flash")
    mocker.patch.object(BootloaderConnection, "_flash_segment")
    mocker.patch.object(BootloaderConnection, "_checksum")
    mocker.patch.object(BootloaderConnection, "_self_verify")

    mock_boot.flash("test/test.hex")
    mock_boot._flash_segment.assert_called()


def test_flash_out_of_range(mock_boot, mocker):
    mocker.patch.object(
        BootloaderConnection,
        "read_version",
        mock_read_version,
    )

    def mock_get_memory_address_range_illegal(*args):
        return HEXFILE.segments()[0][0], HEXFILE.segments()[0][1]

    mocker.patch.object(
        BootloaderConnection,
        "_get_memory_address_range",
        mock_get_memory_address_range_illegal,
    )

    mocker.patch.object(BootloaderConnection, "_erase_flash")
    mocker.patch.object(BootloaderConnection, "_flash_segment")
    mocker.patch.object(BootloaderConnection, "_self_verify")

    mock_boot.flash("test/test.hex")
    mock_boot._flash_segment.assert_not_called()


def test_reset(mock_boot, mock_serial):
    mock_serial.stub(
        receive_bytes=bytes(CommandPacket(command=BootCommand.RESET_DEVICE)),
        send_bytes=bytes(
            ChecksumPacket(
                command=BootCommand.RESET_DEVICE, success=BootResponse.SUCCESS
            )
        ),
    )
    mock_boot.reset()


def test_read_flash(mock_boot):
    with pytest.raises(NotImplementedError):
        mock_boot._read_flash()


def test_check_response():
    command_packet = CommandPacket(command=BootCommand.ERASE_FLASH)
    response_packet = VersionResponsePacket(command=BootCommand.ERASE_FLASH)
    BootloaderConnection._check_response(command_packet, response_packet)


def test_check_response_unexpected():
    command_packet = CommandPacket(command=BootCommand.CALC_CHECKSUM)
    response_packet = ChecksumPacket(command=BootCommand.ERASE_FLASH)
    with pytest.raises(McbootflashException):
        BootloaderConnection._check_response(command_packet, response_packet)


def test_check_response_bad_address():
    command_packet = CommandPacket(command=BootCommand.ERASE_FLASH)
    response_packet = ChecksumPacket(
        command=BootCommand.ERASE_FLASH, success=BootResponse.BAD_ADDRESS
    )
    with pytest.raises(BadAddress):
        BootloaderConnection._check_response(command_packet, response_packet)


def test_check_response_bad_length():
    command_packet = CommandPacket(command=BootCommand.ERASE_FLASH)
    response_packet = ChecksumPacket(
        command=BootCommand.ERASE_FLASH, success=BootResponse.BAD_LENGTH
    )
    with pytest.raises(BadLength):
        BootloaderConnection._check_response(command_packet, response_packet)


def test_check_response_verify_fail():
    command_packet = CommandPacket(command=BootCommand.SELF_VERIFY)
    response_packet = ChecksumPacket(
        command=BootCommand.SELF_VERIFY, success=BootResponse.VERIFY_FAIL
    )
    with pytest.raises(VerifyFail):
        BootloaderConnection._check_response(command_packet, response_packet)


def test_check_response_unsupported_command():
    command_packet = CommandPacket(command=BootCommand.ERASE_FLASH)
    response_packet = ChecksumPacket(
        command=BootCommand.ERASE_FLASH, success=BootResponse.UNSUPPORTED_COMMAND
    )
    with pytest.raises(UnsupportedCommand):
        BootloaderConnection._check_response(command_packet, response_packet)


def test_print_progress_create_bar():
    boot = BootloaderConnection()
    boot._print_progress(0, 100)
    assert boot._bar is not None


def test_print_progress_update_bar():
    boot = BootloaderConnection()
    boot._print_progress(0, 100)
    boot._print_progress(50, 100)
    assert boot._bar.value == 50


def test_print_progress_destroy_bar():
    boot = BootloaderConnection()
    boot._print_progress(0, 100)
    boot._print_progress(100, 100)
    assert boot._bar is None
