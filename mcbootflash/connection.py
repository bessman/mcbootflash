import logging
from dataclasses import dataclass
from typing import Tuple, Union

from intelhex import IntelHex  # type: ignore[import]
from serial import Serial  # type: ignore[import]

from mcbootflash.error import (
    BootloaderError,
    FlashEraseError,
    FlashWriteError,
    ChecksumError,
)
from mcbootflash.protocol import (
    FLASH_UNLOCK_KEY,
    BootCommand,
    BootResponseCode,
    ChecksumPacket,
    CommandPacket,
    ResponsePacket,
    VersionResponsePacket,
    MemoryRangePacket,
)

logger = logging.getLogger(__name__)


@dataclass
class BootloaderAttributes:
    version: int
    max_packet_length: int
    device_id: int
    erase_size: int
    write_size: int
    program_start: int
    program_end: int

    @property
    def legal_range(self) -> range:
        """Return range of address which can be written to."""
        # Final address is legal.
        return range(self.program_start, self.program_end + 1)


class BootloaderConnection(Serial):  # type: ignore # pylint: disable=too-many-ancestors
    """Communication interface to device running MCC 16-bit bootloader."""

    def __init__(self, **kwargs: str):
        super().__init__(**kwargs)
        self.hexfile: Union[None, IntelHex] = None

    def flash(self, hexfile: str) -> None:
        """Flash application firmware.

        Parameters
        ----------
        hexfile : str
            An Intel HEX-file containing application firmware.

        Raises
        ------
        FlashEraseError
        FlashWriteError
        ChecksumError
        BootloaderError
        """
        self.hexfile = IntelHex(hexfile)
        boot_attrs = BootloaderAttributes(
            *self.read_version(), *self._get_memory_address_range()
        )
        self._erase_flash(
            boot_attrs.program_start,
            boot_attrs.program_end,
            boot_attrs.erase_size,
        )

        for segment in self.hexfile.segments():
            # Since the MCU uses 16-bit instructions, each "address" in the
            # (8-bit) hex file is actually only half an address. Therefore, we
            # need to divide by two to get the actual address.
            if (segment[0] // 2 in boot_attrs.legal_range) and (
                segment[1] // 2 in boot_attrs.legal_range
            ):
                logger.info(
                    "Flashing segment "
                    f"{self.hexfile.segments().index(segment)}, "
                    f"[{segment[0]:#08x}:{segment[1]:#08x}]."
                )
                self._flash_segment(
                    segment,
                    boot_attrs.max_packet_length,
                    boot_attrs.write_size,
                )
            else:
                logger.info(
                    f"Segment {self.hexfile.segments().index(segment)} "
                    "ignored; not in legal range "
                    f"([{segment[0] // 2:#08x}:{segment[1] // 2:#08x}] vs. "
                    f"[{boot_attrs.legal_range[0]:#08x}:"
                    f"{boot_attrs.legal_range[-1]:#08x}])."
                )

        self._self_verify()

    def _flash_segment(
        self, segment: Tuple[int, int], max_packet_length: int, write_size: int
    ) -> None:
        chunk_size = max_packet_length - CommandPacket.get_size()
        chunk_size -= chunk_size % write_size
        chunk_size //= 2
        total_bytes = segment[1] - segment[0]
        written_bytes = 0
        # If (segment[1] - segment[0]) % write_size != 0, writing the final
        # chunk will fail. However, I have seen no example where it's not,
        # so not adding code to check for now (YAGNI).
        for addr in range(segment[0] // 2, segment[1] // 2, chunk_size):
            hex_low = addr * 2
            hex_high = (addr + chunk_size) * 2
            chunk = self.hexfile[hex_low:hex_high]  # type: ignore[index]
            self._write_flash(addr, chunk.tobinstr())
            self._checksum(addr, len(chunk))
            written_bytes += len(chunk)
            logger.info(
                f"{written_bytes} bytes written of {total_bytes} "
                f"({written_bytes / total_bytes * 100:.2f}%)."
            )

    @staticmethod
    def _check_response(
        command_packet: CommandPacket,
        response_packet: Union[VersionResponsePacket, ResponsePacket],
    ) -> None:
        """Check that response is not an error."""
        if response_packet.command != command_packet.command:
            logger.error(
                "Unexpected response.\n"
                f"Command:  {bytes(command_packet)!r}\n"
                f"Response: {bytes(response_packet)!r}"
            )
            raise BootloaderError("Unexpected response.")

    def read_version(self) -> Tuple[int, int, int, int, int]:
        """Read bootloader version and some other useful information.

        Returns
        -------
        version : int
        max_packet_length : int
            The maximum size of a single packet sent to the bootloader,
            including both the command and associated data.
        device_id : int
        erase_size : int
            Flash page size. When erasing flash memory, the number of bytes to
            be erased must align with a flash page.
        write_size : int
            Write block size. When writing to flash, the number of bytes to be
            written must align with a write block.
        """
        read_version_command = CommandPacket(command=BootCommand.READ_VERSION)
        self.write(bytes(read_version_command))
        read_version_response = VersionResponsePacket.from_serial(self)
        self._check_response(read_version_command, read_version_response)
        logger.info(
            "Got bootloader attributes:\n"
            f"Max packet length: {read_version_response.max_packet_length:#04x}\n"
            f"Erase size:        {read_version_response.erase_size:#04x}\n"
            f"Write size:        {read_version_response.write_size:#04x}"
        )
        return (
            read_version_response.version,
            read_version_response.max_packet_length,
            read_version_response.device_id,
            read_version_response.erase_size,
            read_version_response.write_size,
        )

    def _get_memory_address_range(self) -> Tuple[int, int]:
        mem_range_command = CommandPacket(command=BootCommand.GET_MEMORY_ADDRESS_RANGE)
        self.write(bytes(mem_range_command))
        mem_range_response = MemoryRangePacket.from_serial(self)
        self._check_response(mem_range_command, mem_range_response)
        logger.info(
            "Got program memory range: "
            f"{mem_range_response.program_start:#08x}:"
            f"{mem_range_response.program_end:#08x}."
        )
        return mem_range_response.program_start, mem_range_response.program_end

    def _erase_flash(
        self, start_address: int, end_address: int, erase_size: int
    ) -> None:
        erase_flash_command = CommandPacket(
            command=BootCommand.ERASE_FLASH,
            data_length=(end_address - start_address) // erase_size,
            unlock_sequence=FLASH_UNLOCK_KEY,
            address=start_address,
        )
        self.write(bytes(erase_flash_command))
        erase_flash_response = ResponsePacket.from_serial(self)

        if erase_flash_response.success != BootResponseCode.SUCCESS:
            logger.error(
                "Flash erase failed: "
                f"{BootResponseCode(erase_flash_response.success).name}."
            )
            raise FlashEraseError(BootResponseCode(erase_flash_response.success).name)
        self._check_response(erase_flash_command, erase_flash_response)
        logger.info(f"Erased flash area {start_address:#08x}:{end_address:#08x}.")

    def _write_flash(self, address: int, data: bytes) -> None:
        write_flash_command = CommandPacket(
            command=BootCommand.WRITE_FLASH,
            data_length=len(data),
            unlock_sequence=FLASH_UNLOCK_KEY,
            address=address,
        )
        self.write(bytes(write_flash_command) + data)
        write_flash_response = ResponsePacket.from_serial(self)

        if write_flash_response.success != BootResponseCode.SUCCESS:
            logger.error(
                f"Failed to write {len(data)} bytes to {address:#08x}: "
                f"{BootResponseCode(write_flash_response.success).name}."
            )
            raise FlashWriteError(BootResponseCode(write_flash_response.success).name)
        self._check_response(write_flash_command, write_flash_response)
        logger.debug(f"Wrote {len(data)} bytes to {address:#08x}.")

    def _self_verify(self) -> None:
        self_verify_command = CommandPacket(command=BootCommand.SELF_VERIFY)
        self.write(bytes(self_verify_command))
        self_verify_response = ResponsePacket.from_serial(self)

        if self_verify_response.success != BootResponseCode.SUCCESS:
            logger.error(
                "Self verify failed: "
                f"{BootResponseCode(self_verify_response.success).name}."
            )
            raise BootloaderError(BootResponseCode(self_verify_response.success).name)
        self._check_response(self_verify_command, self_verify_response)
        logger.info("Self verify OK.")

    def _get_checksum(self, address: int, length: int) -> int:
        calculcate_checksum_command = CommandPacket(
            command=BootCommand.CALC_CHECKSUM,
            data_length=length,
            address=address,
        )
        self.write(bytes(calculcate_checksum_command))
        calculate_checksum_response = ChecksumPacket.from_serial(self)

        if calculate_checksum_response.success != BootResponseCode.SUCCESS:
            logger.error(
                "Failed to get checksum: "
                f"{BootResponseCode(calculate_checksum_response.success).name}"
            )
            raise BootloaderError(
                BootResponseCode(calculate_checksum_response.success).name
            )

        self._check_response(calculcate_checksum_command, calculate_checksum_response)
        return calculate_checksum_response.checksum

    def _calculate_checksum(self, address: int, length: int) -> int:
        checksum = 0
        for i in range(address, address + length, 4):
            data = self.hexfile[i : i + 4].tobinstr()  # type: ignore[index]
            checksum += int.from_bytes(data, byteorder="little") & 0xFFFF
            checksum += (int.from_bytes(data, byteorder="little") >> 16) & 0xFF
        return checksum & 0xFFFF

    def _checksum(self, address: int, length: int) -> None:
        """Compare checksums calculated locally and onboard device.

        Parameters
        ----------
        address : int
            Address from which to start checksum.
        length : int
            Number of bytes to checksum.
        """
        checksum1 = self._calculate_checksum(address * 2, length)
        checksum2 = self._get_checksum(address, length)
        if checksum1 != checksum2:
            logger.error(f"Checksum mismatch: {checksum1} != {checksum2}.")
            raise ChecksumError
        logger.debug(f"Checksum OK: {checksum1}.")

    def reset(self) -> None:
        """Reset device."""
        reset_command = CommandPacket(command=BootCommand.RESET_DEVICE)
        self.write(bytes(reset_command))
        reset_response = ResponsePacket.from_serial(self)
        self._check_response(reset_command, reset_response)

    def _read_flash(self) -> None:
        raise NotImplementedError
