"""Flash firmware to devices running Microchip's 16-bit bootloader."""
from .connection import Bootloader
from .error import BootloaderError
from .flashing import flash, get_parser

__all__ = ["Bootloader", "BootloaderError", "flash", "get_parser"]

__version__ = "6.1.0"
