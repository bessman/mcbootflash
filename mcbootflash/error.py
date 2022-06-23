from mcbootflash.protocol import BootResponse
"""Exceptions raised by mcbootflash."""


class BootloaderError(Exception):
    """Base class for mccflash exceptions.

    Raised when a negative response code is received and no derived exception
    applies.
    """


class UnsupportedCommand(BootloaderError):
    """Raised if the bootloader does not recognize the most recently sent command."""


class BadAddress(BootloaderError):
    """Raised if a write operation is attempted outside legal range."""


class BadLength(BootloaderError):
    """Raised if the command packet and associated data is longer than permitted."""


class VerifyFail(BootloaderError):
    """Raised if no program is detected in the program memory range."""


class ChecksumError(BootloaderError):
    """Raised if the device checksum does not match the written hex file."""


EXCEPTIONS = {
    BootResponse.UNSUPPORTED_COMMAND: UnsupportedCommand,
    BootResponse.BAD_ADDRESS: BadAddress,
    BootResponse.BAD_LENGTH: BadLength,
    BootResponse.VERIFY_FAIL: VerifyFail,
}
