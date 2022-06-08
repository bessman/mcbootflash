class BootloaderError(Exception):
    """Base class for mccflash exceptions.

    Raised when a negative response code is received and no derived exception
    applies.
    """


class FlashEraseError(BootloaderError):
    """Raised if an attempt to erase flash memory failed."""


class FlashWriteError(BootloaderError):
    """Raised if an attempt to write to flash failed."""


class ChecksumError(FlashWriteError):
    """Raised if the device checksum does not match the written hex file."""
