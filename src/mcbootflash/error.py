"""Exceptions raised by mcbootflash."""
__all__ = [
    "BadAddress",
    "BadLength",
    "BootloaderError",
    "ChecksumError",
    "ConnectionFailure",
    "FlashEraseFail",
    "McbootflashException",
    "NoData",
    "UnexpectedResponse",
    "UnsupportedCommand",
    "VerifyFail",
]


class McbootflashException(Exception):
    """Base class for mcbootflash exceptions."""


class BootloaderError(McbootflashException):
    """Base class for exceptions that map to a specific BootResponse error code."""


class UnsupportedCommand(BootloaderError):
    """Raised if ResponsePacket.success is BootResponse.UNSUPPORTED_COMMAND.

    This means that the bootloader did not recognize the most recently sent command.
    """


class BadAddress(BootloaderError):
    """Raised if ResponsePacket.success is BootResponse.BAD_ADDRESS.

    This means an operation was attempted outside of the program memory range.
    """


class BadLength(BootloaderError):
    """Raised if ResponsePacket.success is BootResponse.BAD_LENGTH.

    This means that the size of the command packet plus associated data was greater
    than permitted.
    """


class VerifyFail(BootloaderError):
    """Raised if ResponsePacket.success is BootResponse.VERIFY_FAIL.

    This means that no program was detected in the program memory range.
    """


class ChecksumError(McbootflashException):
    """Raised in case of mismatch between local and remote checksums."""


class FlashEraseFail(McbootflashException):
    """Raised if a program is still detected in flash memory after an erase attempt."""


class UnexpectedResponse(McbootflashException):
    """Raised if the command fields of a Command/Response packet pair do not match."""


class ConnectionFailure(McbootflashException):
    """Raised if the connection to the bootloader cannot be established or is lost."""


class NoData(McbootflashException):
    """Raised if asked to flash a HEX file which contains no suitable data.

    Specifically, the HEX file must contain at least one memory segment that fits
    entirely within the program memory range specified by the bootloader.
    """
