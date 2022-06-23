"""Exceptions raised by mcbootflash."""
__all__ = [
    "BadAddress",
    "BadLength",
    "BootloaderError",
    "ChecksumError",
    "McbootflashException",
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
