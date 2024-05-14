# mcbootflash

![build](https://github.com/bessman/mcbootflash/actions/workflows/main.yml/badge.svg)
[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://bessman.github.io/mcbootflash/)
[![PyPI](https://img.shields.io/pypi/v/mcbootflash.svg)](https://pypi.org/project/mcbootflash/)
[![License](https://img.shields.io/pypi/l/mcbootflash)](https://mit-license.org/)

## What

Mcbootflash is a Python tool for flashing firmware to 16-bit Microchip MCUs and DSCs
from the PIC24 and dsPIC33 families of devices, which are running a
[bootloader](https://www.microchip.com/en-us/software-library/16-bit-bootloader)
generated by the MPLAB Code Configurator tool.

Mcbootflash is intended to be a drop-in replacement for Microchip's official tool, the
Unified Bootloader Host Application (UBHA).

## Why

Mcbootflash is:

### Scriptable

As a command-line application, mcbootflash is easily scriptable.

### Extensible

In addition to its command-line interface, mcbootflash can be used as a library by
applications wanting to implement firmware flashing as part of a larger suite of
features.

### Free and Open Source

Mcbootflash is distributed under the MIT license.

## Installation

`pip install mcbootflash`

## Usage

Mcbootflash can be used as both a command-line application and a library.

### Command-line

```shellsession
$ mcbootflash --help
usage: mcbootflash [-h] -p PORT -b BAUDRATE [-t TIMEOUT] [-c] [-r] [-v] [-q] [--version] hexfile

Flash firmware over serial connection to a device running Microchip's 16-bit bootloader.

positional arguments:
  hexfile               a HEX file containing application firmware

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  serial port connected to the device you want to flash
  -b BAUDRATE, --baudrate BAUDRATE
                        symbol rate of device's serial bus
  -t TIMEOUT, --timeout TIMEOUT
                        try to read data from the bus for this many seconds before giving up
  -c, --checksum        verify flashed data by checksumming after write
  -r, --reset           reset device after flashing is complete
  -v, --verbose         print debug messages
  -q, --quiet           suppress output
  --version             show program's version number and exit
```

#### Example

```shellsession
$ mcbootflash --port /dev/ttyUSB0 --baudrate 460800 firmware.hex
Connecting to bootloader...
Erasing program area...
Flashing firmware.hex...
100%  88.7 KiB |########################################| Elapsed Time: 0:00:05
Self verify OK
```

### Library

When using mcbootflash as a library, typical workflow looks something like this:

``` py
import mcbootflash as bf
import serial


# Connect to a device in bootloader mode.
connection = serial.Serial(port=<PORT>, baudrate=<BAUDRATE>, timeout=<TIMEOUT>)
# Query its attributes.
bootattrs = bf.get_boot_attrs(connection)
# Load the firmware image and split it into chunks.
total_bytes, chunks = bf.chunked(hexfile=<HEXFILE_PATH_STRING>, bootattrs)
# Erase the device's program memory area.
bf.erase_flash(connection, bootattrs.memory_range, bootattrs.erase_size)

# Write the firmware chunks to the bootloader in a loop.
for chunk in chunks:
    bf.write_flash(connection, chunk)

    # Optionally, check that the write is OK by checksumming.
    bf.checksum(connection, chunk)

    # At this point, you may want to give an indication of the flashing progress,
    # like updating a progress bar.

# Verify that the new application is detected.
bf.self_verify(connection)
```

See also the [API Reference](https://bessman.github.io/mcbootflash/api/).