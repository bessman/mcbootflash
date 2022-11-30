# mcbootflash

![build](https://github.com/bessman/mcbootflash/actions/workflows/main.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/mcbootflash/badge/?version=latest)](https://mcbootflash.readthedocs.io/en/latest/?badge=latest)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b0cdb1c0b3b94171866fbfc4489316be)](https://www.codacy.com/gh/bessman/mcbootflash/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bessman/mcbootflash&amp;utm_campaign=Badge_Grade)
[![Codecov](https://codecov.io/gh/bessman/mcbootflash/branch/main/graph/badge.svg)](https://codecov.io/gh/bessman/mcbootflash)


Mcbootflash is a tool for flashing firmware to 16-bit Microchip MCUs and DSPs
from the PIC24 and dsPIC33 families of devices, which are running a
[bootloader](https://www.microchip.com/en-us/software-library/16-bit-bootloader)
generated by the MPLAB Code Configurator tool.

Microchip provides an official GUI tool for this purpose, called the
Unified Bootloader Host Application. Mcbootflash is intended to be a
drop-in replacement, with some differences:

-   No GUI
-   Free and open source
-   Written in Python instead of Java

Additionally, mcbootflash can be used as a library by applications which
want to implement firmware flashing as part of a larger suite of features.
See the documentation for details.

## Installation

`pip install mcbootflash`

## Usage

Once installed, mcbootflash can be run from the command line:

```console
$ mcbootflash --port=/dev/ttyUSB0 --baudrate=460800 firmware.hex
  Connecting to bootloader...
  Connected
  Flashing firmware.hex
  Existing application detected, erasing...
  No application detected; flash erase successful
  100%  88.7 KiB |########################################| Elapsed Time: 0:00:05
  Self verify OK
```

## Copyright

MIT License, (C) 2022 Alexander Bessman
