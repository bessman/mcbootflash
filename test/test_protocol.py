import pytest

import mock_serial
from serial import Serial

from mcbootflash import (
    BootCommand,
    BootResponseCode,
    CommandPacket,
    FLASH_UNLOCK_KEY,
    MemoryRangePacket,
    ResponsePacket,
    VersionResponsePacket,
)


command_packet = CommandPacket(
    command=BootCommand.WRITE_FLASH.value,
    data_length=8,
    unlock_sequence=FLASH_UNLOCK_KEY,
    address=0x1234,
)
command_bytes = b"\x02\x08\x00U\x00\xaa\x004\x12\x00\x00"


def test_command_packet_to_bytes():
    assert bytes(command_packet) == command_bytes


version_response_packet = VersionResponsePacket(
    command=BootCommand.READ_VERSION.value,
    version=0x0102,
    max_packet_length=0x100,
    device_id=0x3456,
    erase_size=2048,
    write_size=8,
)
version_response_bytes = (
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x01\x00\x01\x00\x00V4"
    b"\x00\x00\x00\x08\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
)


def test_version_packet_from_serial(mock_serial):
    interface = Serial(port=mock_serial.port)
    stub = mock_serial.stub(
        receive_bytes=b"\x00",
        send_bytes=version_response_bytes,
    )
    interface.write(b"\x00")
    retval = VersionResponsePacket.from_serial(interface=interface)
    assert retval == version_response_packet
