import pytest

import intelhex
import mock_serial

from mcbootflash.connection import BootloaderConnection
from mcbootflash.error import (
    BootloaderError,
    ChecksumError,
    FlashEraseError,
    FlashWriteError,
)
from mcbootflash.protocol import (
    BootCommand,
    BootResponseCode,
    ChecksumPacket,
    CommandPacket,
    FLASH_UNLOCK_KEY,
    MemoryRangePacket,
    ResponsePacket,
    VersionResponsePacket,
)


@pytest.fixture
def mock_boot(mock_serial):
    boot = BootloaderConnection(port=mock_serial.port, timeout=0.1)
    yield boot
    boot.close()


def test_read_version(mock_boot, mock_serial):
    expected = {
        "version": 0x0102,
        "max_packet_length": 0x0100,
        "device_id": 0x3456,
        "erase_size": 0x0800,
        "write_size": 0x08,
    }
    mock_serial.stub(
        receive_bytes=bytes(CommandPacket(command=BootCommand.READ_VERSION)),
        send_bytes=bytes(
            VersionResponsePacket(command=BootCommand.READ_VERSION, **expected)
        ),
    )
    assert mock_boot.read_version() == tuple(expected.values())


def test_get_memory_address_range(mock_boot, mock_serial):
    expected = {"program_start": 0x2000, "program_end": 0x4000}
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(command=BootCommand.GET_MEMORY_ADDRESS_RANGE)
        ),
        send_bytes=bytes(
            MemoryRangePacket(
                command=BootCommand.GET_MEMORY_ADDRESS_RANGE,
                success=BootResponseCode.SUCCESS.value,
                **expected
            )
        ),
    )
    assert mock_boot._get_memory_address_range() == tuple(expected.values())


def test_erase_flash(mock_boot, mock_serial):
    start_address = 0x2000
    end_address = 0x4000
    erase_size = 0x0800
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.ERASE_FLASH,
                data_length=int((end_address - start_address) // erase_size),
                unlock_sequence=FLASH_UNLOCK_KEY,
                address=start_address,
            )
        ),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.ERASE_FLASH,
                success=BootResponseCode.SUCCESS,
            )
        ),
    )
    # BootloaderConnection._erase_flash returns nothing and all side effects
    # are bootloader-side. The only thing we can test is that no unexpected
    # exception occurs, hence no assert.
    mock_boot._erase_flash(start_address, end_address, erase_size)


def test_erase_flash_fail(mock_boot, mock_serial):
    start_address = 0x2000
    end_address = 0x4000
    erase_size = 0x0800
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.ERASE_FLASH,
                data_length=int((end_address - start_address) // erase_size),
                unlock_sequence=FLASH_UNLOCK_KEY,
                address=start_address,
            )
        ),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.ERASE_FLASH,
                success=BootResponseCode.BAD_ADDRESS,
            )
        ),
    )
    with pytest.raises(FlashEraseError):
        mock_boot._erase_flash(start_address, end_address, erase_size)


def test_write_flash(mock_boot, mock_serial):
    address = 0x2000
    data = bytes(range(8))
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.WRITE_FLASH,
                data_length=len(data),
                unlock_sequence=FLASH_UNLOCK_KEY,
                address=address,
            )
        ),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.WRITE_FLASH,
                success=BootResponseCode.SUCCESS,
            )
        ),
    )
    mock_boot._write_flash(address, data)


def test_write_flash_fail(mock_boot, mock_serial):
    address = 0x2000
    data = bytes(range(8))
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.WRITE_FLASH,
                data_length=len(data),
                unlock_sequence=FLASH_UNLOCK_KEY,
                address=address,
            )
        ),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.WRITE_FLASH,
                success=BootResponseCode.BAD_ADDRESS,
            )
        ),
    )
    with pytest.raises(FlashWriteError):
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
                success=BootResponseCode.SUCCESS,
            )
        ),
    )
    mock_boot._self_verify()


def test_self_verify_fail(mock_boot, mock_serial):
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.SELF_VERIFY,
            )
        ),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.SELF_VERIFY,
                success=BootResponseCode.VERIFY_FAIL,
            )
        ),
    )
    with pytest.raises(BootloaderError):
        mock_boot._self_verify()


def test_get_checksum(mock_boot, mock_serial):
    address = 0x2000
    length = 0x08
    checksum = 0x060C
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.CALC_CHECKSUM,
                data_length=length,
                address=address,
            )
        ),
        send_bytes=bytes(
            ChecksumPacket(
                command=BootCommand.CALC_CHECKSUM,
                success=BootResponseCode.SUCCESS,
                checksum=checksum,
            )
        ),
    )
    assert mock_boot._get_checksum(address, length) == checksum


def test_get_checksum_fail(mock_boot, mock_serial):
    address = 0x2000
    length = 0x08
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.CALC_CHECKSUM,
                data_length=length,
                address=address,
            )
        ),
        send_bytes=bytes(
            ChecksumPacket(
                command=BootCommand.CALC_CHECKSUM,
                success=BootResponseCode.BAD_ADDRESS,
            )
        ),
    )
    with pytest.raises(BootloaderError):
        mock_boot._get_checksum(address, length)


def test_calculate_checksum(mock_boot):
    mock_boot.hexfile = intelhex.IntelHex("test/test.hex")
    segments = mock_boot.hexfile.segments()
    address = segments[0][0]
    length = segments[0][1] - segments[0][0]
    expected_checksum = 0x10B5
    assert mock_boot._calculate_checksum(address, length) == expected_checksum


def test_checksum(mock_boot, mock_serial):
    mock_boot.hexfile = intelhex.IntelHex("test/test.hex")
    segments = mock_boot.hexfile.segments()
    address = segments[0][0]
    length = segments[0][1] - segments[0][0]
    expected_checksum = 0x10B5
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.CALC_CHECKSUM,
                data_length=length,
                address=address // 2,
            )
        ),
        send_bytes=bytes(
            ChecksumPacket(
                command=BootCommand.CALC_CHECKSUM,
                success=BootResponseCode.SUCCESS,
                checksum=expected_checksum,
            )
        ),
    )
    mock_boot._checksum(address // 2, length)


def test_checksum_fail(mock_boot, mock_serial):
    mock_boot.hexfile = intelhex.IntelHex("test/test.hex")
    segments = mock_boot.hexfile.segments()
    address = segments[0][0]
    length = segments[0][1] - segments[0][0]
    expected_checksum = 0x10B5
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.CALC_CHECKSUM,
                data_length=length,
                address=address // 2,
            )
        ),
        send_bytes=bytes(
            ChecksumPacket(
                command=BootCommand.CALC_CHECKSUM,
                success=BootResponseCode.SUCCESS,
                checksum=0,
            )
        ),
    )
    with pytest.raises(ChecksumError):
        mock_boot._checksum(address // 2, length)


def test_flash_segment(mock_boot, mock_serial):
    mock_boot.hexfile = intelhex.IntelHex("test/test.hex")
    mock_boot.max_packet_length = 0x13
    mock_boot.write_size = 8
    for addr in range(*mock_boot.hexfile.segments()[0], 8):
        data = mock_boot.hexfile[addr : addr + 8]
        mock_serial.stub(
            receive_bytes=bytes(
                CommandPacket(
                    command=BootCommand.WRITE_FLASH,
                    data_length=len(data),
                    unlock_sequence=FLASH_UNLOCK_KEY,
                    address=addr // 2,
                )
            )
            + data.tobinstr(),
            send_bytes=bytes(
                ResponsePacket(
                    command=BootCommand.WRITE_FLASH,
                    success=BootResponseCode.SUCCESS,
                )
            ),
        )
        mock_serial.stub(
            receive_bytes=bytes(
                CommandPacket(
                    command=BootCommand.CALC_CHECKSUM,
                    data_length=len(data),
                    address=addr // 2,
                )
            ),
            send_bytes=bytes(
                ChecksumPacket(
                    command=BootCommand.CALC_CHECKSUM,
                    success=BootResponseCode.SUCCESS,
                    checksum=mock_boot._calculate_checksum(
                        address=addr, length=len(data)
                    ),
                ),
            ),
        )
    mock_boot._flash_segment(mock_boot.hexfile.segments()[0])


def test_flash(mock_boot, mock_serial):
    max_packet_length = 0x0013
    erase_size = 0x0020
    write_size = 0x08
    mock_boot.hexfile = intelhex.IntelHex("test/test.hex")
    mock_serial.stub(
        receive_bytes=bytes(CommandPacket(command=BootCommand.READ_VERSION)),
        send_bytes=bytes(
            VersionResponsePacket(
                command=BootCommand.READ_VERSION,
                version=0x0102,
                max_packet_length=max_packet_length,
                device_id=0x3456,
                erase_size=erase_size,
                write_size=write_size,
            )
        ),
    )
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(command=BootCommand.GET_MEMORY_ADDRESS_RANGE)
        ),
        send_bytes=bytes(
            MemoryRangePacket(
                command=BootCommand.GET_MEMORY_ADDRESS_RANGE,
                success=BootResponseCode.SUCCESS,
                program_start=mock_boot.hexfile.segments()[0][0] // 2,
                program_end=mock_boot.hexfile.segments()[0][1] // 2 + 2,
            )
        ),
    )
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.ERASE_FLASH,
                data_length=(
                    (
                        mock_boot.hexfile.segments()[0][1] // 2
                        - mock_boot.hexfile.segments()[0][0] // 2
                    )
                    // erase_size
                ),
                unlock_sequence=FLASH_UNLOCK_KEY,
                address=mock_boot.hexfile.segments()[0][0] // 2,
            )
        ),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.ERASE_FLASH,
                success=BootResponseCode.SUCCESS,
            )
        ),
    )

    for addr in range(*mock_boot.hexfile.segments()[0], write_size):
        data = mock_boot.hexfile[addr : addr + write_size]
        mock_serial.stub(
            receive_bytes=bytes(
                CommandPacket(
                    command=BootCommand.WRITE_FLASH,
                    data_length=len(data),
                    unlock_sequence=FLASH_UNLOCK_KEY,
                    address=addr // 2,
                )
            )
            + data.tobinstr(),
            send_bytes=bytes(
                ResponsePacket(
                    command=BootCommand.WRITE_FLASH,
                    success=BootResponseCode.SUCCESS,
                )
            ),
        )
        mock_serial.stub(
            receive_bytes=bytes(
                CommandPacket(
                    command=BootCommand.CALC_CHECKSUM,
                    data_length=len(data),
                    address=addr // 2,
                )
            ),
            send_bytes=bytes(
                ChecksumPacket(
                    command=BootCommand.CALC_CHECKSUM,
                    success=BootResponseCode.SUCCESS,
                    checksum=mock_boot._calculate_checksum(
                        address=addr, length=len(data)
                    ),
                ),
            ),
        )

    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.SELF_VERIFY,
            )
        ),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.SELF_VERIFY,
                success=BootResponseCode.SUCCESS,
            )
        ),
    )
    mock_boot.flash("test/test.hex")


def test_flash_out_of_range(mock_boot, mock_serial):
    max_packet_length = 0x0013
    erase_size = 0x0020
    write_size = 0x08
    mock_boot.hexfile = intelhex.IntelHex("test/test.hex")
    mock_serial.stub(
        receive_bytes=bytes(CommandPacket(command=BootCommand.READ_VERSION)),
        send_bytes=bytes(
            VersionResponsePacket(
                command=BootCommand.READ_VERSION,
                version=0x0102,
                max_packet_length=max_packet_length,
                device_id=0x3456,
                erase_size=erase_size,
                write_size=write_size,
            )
        ),
    )
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(command=BootCommand.GET_MEMORY_ADDRESS_RANGE)
        ),
        send_bytes=bytes(
            MemoryRangePacket(
                command=BootCommand.GET_MEMORY_ADDRESS_RANGE,
                success=BootResponseCode.SUCCESS,
                program_start=mock_boot.hexfile.segments()[0][0] // 2,
                program_end=mock_boot.hexfile.segments()[0][1] // 2,
            )
        ),
    )
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.ERASE_FLASH,
                data_length=(
                    (
                        mock_boot.hexfile.segments()[0][1] // 2
                        - mock_boot.hexfile.segments()[0][0] // 2
                    )
                    // erase_size
                ),
                unlock_sequence=FLASH_UNLOCK_KEY,
                address=mock_boot.hexfile.segments()[0][0] // 2,
            )
        ),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.ERASE_FLASH,
                success=BootResponseCode.SUCCESS,
            )
        ),
    )
    mock_serial.stub(
        receive_bytes=bytes(
            CommandPacket(
                command=BootCommand.SELF_VERIFY,
            )
        ),
        send_bytes=bytes(
            ResponsePacket(
                command=BootCommand.SELF_VERIFY,
                success=BootResponseCode.SUCCESS,
            )
        ),
    )
    mock_boot.flash("test/test.hex")
