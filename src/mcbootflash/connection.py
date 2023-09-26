# noqa: D100
import logging
import sys
from struct import error as structerror
from typing import Any, Dict, Tuple, Type, Union

import bincopy  # type: ignore[import]
from serial import Serial  # type: ignore[import]

from mcbootflash.error import (
    BadAddress,
    BadLength,
    BootloaderError,
    UnsupportedCommand,
    VerifyFail,
)
from mcbootflash.protocol import (
    Checksum,
    Command,
    CommandCode,
    MemoryRange,
    Response,
    ResponseBase,
    ResponseCode,
    Version,
)

if sys.version_info.minor < 9:
    from typing import Callable
else:
    from collections.abc import Callable

_logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int], None]


class Bootloader:
    """Communication interface to device running MCC 16-bit bootloader.

    Parameters
    ----------
    port : str
        Serial port name. Typically /dev/ttyUSBx or /dev/ttyACMx on Posix, or COMx on
        Windows.
    **kwargs, optional
        Any additional arguments for the serial.Serial constructor.
    """

    # Is this key always the same? Perhaps generated by MCC during code generation?
    # If this key is incorrect, flash write operations will fail silently.
    _FLASH_UNLOCK_KEY = 0x00AA0055

    def __init__(self, port: str, **kwargs: Any):
        self.interface = Serial(port=port, **kwargs)
        _logger.info("Connecting to bootloader...")
        try:
            (
                _,  # version
                self._max_packet_length,
                _,  # device_id
                self._erase_size,
                self._write_size,
            ) = self._read_version()
            self._memory_range = self._get_memory_address_range()
        except structerror as exc:
            raise BootloaderError("No response from bootloader") from exc
        _logger.info("Connected")
        self._disable_checksum = False
        self._most_recent_command: Union[None, Command] = None

    def flash(
        self,
        hexfile: str,
        progress_callback: Union[None, ProgressCallback] = None,
    ) -> None:
        """Flash application firmware.

        Parameters
        ----------
        hexfile : str
            Path to a HEX-file containing application firmware.
        progress_callback : Callable[[int, int], None] (optional)
            A callable which takes the number of bytes written so far as its first
            argument, and the total number of bytes to write as its second argument.
            The callable returns None. If no callback is provided, progress is not
            reported.

        Raises
        ------
        BootloaderError
            If HEX-file cannot be flashed.
        """
        path = hexfile
        hexdata = bincopy.BinFile()
        hexdata.add_microchip_hex_file(path)
        hexdata.crop(*self._memory_range)

        if not hexdata.segments:
            raise BootloaderError(
                "HEX file contains no data that fits entirely within program memory"
            )

        _logger.info(f"Flashing {path}")
        self.erase_flash()
        chunk_size = self._max_packet_length - Command.get_size()
        chunk_size -= chunk_size % self._write_size
        chunk_size //= hexdata.word_size_bytes
        total_bytes = len(hexdata) * hexdata.word_size_bytes
        written_bytes = 0

        for chunk in hexdata.segments.chunks(chunk_size):
            self._write_flash(chunk)
            written_bytes += len(chunk.data)
            _logger.debug(
                f"{written_bytes} bytes written of {total_bytes} "
                f"({written_bytes / total_bytes * 100:.2f}%)"
            )

            if not self._disable_checksum:
                self._checksum(chunk)

            if progress_callback:
                progress_callback(written_bytes, total_bytes)

        self._self_verify()

    def _get_response(self) -> ResponseBase:
        """Get a Response packet.

        Returns
        -------
        packet : ResponseBase
            An instance of a ResponseBase packet or a subclass thereof.
        """
        # Can't read the whole response in one go. Its length depends on whether it's an
        # error or not. Start by reading the command echo to determine the response
        # type.
        response = ResponseBase.from_bytes(self.interface.read(ResponseBase.get_size()))
        _logger.debug(f"RX: {self._format_debug_bytes(bytes(response))}")

        assert isinstance(self._most_recent_command, Command)

        if response.command != self._most_recent_command.command:
            raise BootloaderError("Command code mismatch")

        response_type_map: Dict[CommandCode, Type[ResponseBase]] = {
            CommandCode.READ_VERSION: Version,
            CommandCode.READ_FLASH: Response,
            CommandCode.WRITE_FLASH: Response,
            CommandCode.ERASE_FLASH: Response,
            CommandCode.CALC_CHECKSUM: Checksum,
            CommandCode.RESET_DEVICE: Response,
            CommandCode.SELF_VERIFY: Response,
            CommandCode.GET_MEMORY_ADDRESS_RANGE: MemoryRange,
        }
        response_type = response_type_map[CommandCode(response.command)]

        # READ_VERSION has no 'success' flag.
        if response_type is Version:
            remainder = self.interface.read(
                response_type.get_size() - response.get_size()
            )
            _logger.debug(f"RX: {self._format_debug_bytes(remainder, bytes(response))}")
            return response_type.from_bytes(bytes(response) + remainder)

        success = self.interface.read(1)
        _logger.debug(f"RX: {self._format_debug_bytes(success, bytes(response))}")

        if success[0] != ResponseCode.SUCCESS:
            bootloader_exceptions: Dict[ResponseCode, Type[BootloaderError]] = {
                ResponseCode.UNSUPPORTED_COMMAND: UnsupportedCommand,
                ResponseCode.BAD_ADDRESS: BadAddress,
                ResponseCode.BAD_LENGTH: BadLength,
                ResponseCode.VERIFY_FAIL: VerifyFail,
            }
            raise bootloader_exceptions[success[0]]

        response = Response.from_bytes(bytes(response) + success)
        remainder = self.interface.read(response_type.get_size() - response.get_size())

        if remainder:
            _logger.debug(f"RX: {self._format_debug_bytes(remainder, bytes(response))}")

        response = response_type.from_bytes(bytes(response) + remainder)

        return response

    def _send_and_receive(self, command: Command, data: bytes = b"") -> ResponseBase:
        msg = f"TX: {self._format_debug_bytes(bytes(command))}"
        msg += f" plus {len(data)} data bytes" if data else ""
        _logger.debug(msg)
        self.interface.write(bytes(command) + data)
        self._most_recent_command = command
        response = self._get_response()
        return response

    @staticmethod
    def _format_debug_bytes(debug_bytes: bytes, pad: bytes = b"") -> str:
        padding = " " * len(f"{' '.join(f'{b:02X}' for b in pad)}")
        padding += " " if padding else ""
        return f"{padding}{' '.join(f'{b:02X}' for b in debug_bytes)}"

    def _read_version(self) -> Tuple[int, int, int, int, int]:
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
        read_version_response = self._send_and_receive(
            Command(CommandCode.READ_VERSION)
        )
        assert isinstance(read_version_response, Version)
        _logger.debug("Got bootloader attributes:")
        _logger.debug(f"Max packet length: {read_version_response.max_packet_length}")
        _logger.debug(f"Erase size:        {read_version_response.erase_size}")
        _logger.debug(f"Write size:        {read_version_response.write_size}")

        return (
            read_version_response.version,
            read_version_response.max_packet_length,
            read_version_response.device_id,
            read_version_response.erase_size,
            read_version_response.write_size,
        )

    def _get_memory_address_range(self) -> Tuple[int, int]:
        """Get the program memory range, i.e. the range of writable addresses.

        The returned tuple is suitable for use in `range`, i.e. the upper bound is not
        part of the writable range.
        """
        mem_range_response = self._send_and_receive(
            Command(CommandCode.GET_MEMORY_ADDRESS_RANGE)
        )
        assert isinstance(mem_range_response, MemoryRange)
        _logger.debug(
            "Got program memory range: "
            f"{mem_range_response.program_start:#08x}:"
            f"{mem_range_response.program_end:#08x}"
        )
        # program_end + 2 explanation:
        # +1 because the upper bound reported by the bootloader is inclusive, but we
        # want to use it as a Python range, which is half-open.
        # +1 because the final byte of the final 24-bit instruction is not included in
        # the range reported by the bootloader, but it is still writable.
        return mem_range_response.program_start, mem_range_response.program_end + 2

    def erase_flash(
        self,
        erase_range: Union[None, range] = None,
        force: bool = False,
        verify: bool = True,
    ) -> None:
        """Erase program memory area.

        Parameters
        ----------
        erase_range: range, optional
            Address range to erase. By default the entire program memory is erased.
        force : bool, optional
            By default, flash erase will be skipped if no program is detected in the
            program memory area. Setting `force` to True skips program detection and
            erases regardless of whether a program is present or not.
        verify : bool, optional
            The ERASE_FLASH command may fail silently if the `unlock_sequence` field of
            the command packet is incorrect. By default, this method verifies that the
            erase was successful by checking that no application is detected after the
            erase. Set `verify` to False to skip this check.
        """
        start, *_, end = erase_range if erase_range else range(*self._memory_range)

        if force or self._detect_program():
            _logger.info("Erasing flash...")
            self._erase_flash(start, end + 1)
        else:
            _logger.info("No application detected, skipping flash erase")
            return

        if verify:
            if self._detect_program():
                _logger.debug("An application was detected; flash erase failed")
                _logger.debug("unlock_sequence field may be incorrect")
                raise BootloaderError("Existing application could not be erased")
            _logger.info("No application detected; flash erase successful")

    def _erase_flash(self, start_address: int, end_address: int) -> None:
        # [start, end)
        _logger.debug(f"Erasing addresses {start_address:#08x}:{end_address:#08x}")
        normal_timeout = self.interface.timeout

        if self.interface.timeout is not None:
            self.interface.timeout *= 10  # Erase may take a while.

        self._send_and_receive(
            command=Command(
                command=CommandCode.ERASE_FLASH,
                data_length=(end_address - start_address) // self._erase_size,
                unlock_sequence=self._FLASH_UNLOCK_KEY,
                address=start_address,
            )
        )
        self.interface.timeout = normal_timeout

    def _detect_program(self) -> bool:
        try:
            # Program memory may be empty, which should not be logged as an error.
            _logger.disabled = True
            self._self_verify()
        except VerifyFail:
            return False
        finally:
            _logger.disabled = False
        return True

    def _write_flash(self, chunk: bincopy.Segment) -> None:
        """Write data to bootloader.

        Parameters
        ----------
        chunk : bincopy.Segment
            A bincopy.Segment instance of length no greater than the bootloader's
            max_packet_length attribute.
        """
        # Ensure data length is a multiple of write size.
        padding = b"\xff" * (
            (self._write_size - (len(chunk.data) % self._write_size)) % self._write_size
        )
        _logger.debug(
            f"Writing {len(chunk.data) + len(padding)} bytes to {chunk.address:#08x}"
        )
        self._send_and_receive(
            Command(
                command=CommandCode.WRITE_FLASH,
                data_length=len(chunk.data) + len(padding),
                unlock_sequence=self._FLASH_UNLOCK_KEY,
                address=chunk.address,
            ),
            chunk.data + padding,
        )

    def _self_verify(self) -> None:
        self._send_and_receive(Command(command=CommandCode.SELF_VERIFY))
        _logger.info("Self verify OK")

    def _get_remote_checksum(self, address: int, length: int) -> int:
        checksum_response = self._send_and_receive(
            Command(
                command=CommandCode.CALC_CHECKSUM,
                data_length=length,
                address=address,
            )
        )
        assert isinstance(checksum_response, Checksum)
        return checksum_response.checksum

    @staticmethod
    def _get_local_checksum(chunk: bincopy.Segment) -> int:
        chksum = 0

        for piece in chunk.chunks(
            size=4 // chunk.word_size_bytes,
        ):
            chksum += piece.data[0] + (piece.data[1] << 8) + piece.data[2]

        return chksum & 0xFFFF

    def _checksum(self, chunk: bincopy.Segment) -> None:
        """Compare checksums calculated locally and onboard device.

        Parameters
        ----------
        segment : bincopy.Segment
            HEX segment to checksum.
        """
        # Workaround for bug in bootloader. The bootloader incorrectly raises
        # BAD_ADDRESS when trying to calculate checksums close to the upper bound of the
        # program memory range.
        if (self._memory_range[1] - chunk.address) < len(chunk.data):
            _logger.debug(
                "Too close to upper memory bound, skipping checksum calculation"
            )
            return

        checksum1 = self._get_local_checksum(chunk)

        try:
            checksum2 = self._get_remote_checksum(chunk.address, len(chunk.data))
        except UnsupportedCommand:
            _logger.warning("Bootloader does not support checksums")
            self._disable_checksum = True
            return

        if checksum1 != checksum2:
            _logger.debug(f"Checksum mismatch: {checksum1} != {checksum2}")
            _logger.debug("unlock_sequence field may be incorrect")
            raise BootloaderError("Checksum mismatch while writing")

        _logger.debug(f"Checksum OK: {checksum1}")

    def reset(self) -> None:
        """Reset device."""
        self._send_and_receive(Command(command=CommandCode.RESET_DEVICE))
        _logger.info("Device reset")

    def _read_flash(self) -> None:
        raise NotImplementedError
