"""Exceptions raised by mcbootflash."""


class BootloaderError(Exception):
    """Base class for mcbootflash exceptions.

    Subclasses must map to a specific error response code.
    """


class UnsupportedCommand(BootloaderError):
    """Raised if Response.success is ResponseCode.UNSUPPORTED_COMMAND.

    This means that the bootloader did not recognize the most recently sent command.
    """


class BadAddress(BootloaderError):
    """Raised if Response.success is ResponseCode.BAD_ADDRESS.

    This means an operation was attempted outside of the program memory range.
    """


class BadLength(BootloaderError):
    """Raised if Response.success is ResponseCode.BAD_LENGTH.

    This means that the size of the command packet plus associated data was greater
    than permitted.
    """


class VerifyFail(BootloaderError):
    """Raised if Response.success is ResponseCode.VERIFY_FAIL.

    This means that no program was detected in the program memory range.
    """
