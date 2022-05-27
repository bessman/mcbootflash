# mcbootflash

## Overview

mcbootflash is a tool for flashing firmware to devices running Microchip's
[MCC 16-bit bootloader](https://www.microchip.com/en-us/software-library/16-bit-bootloader).
Microchip provides an official GUI tool for this purpose, called the
Unified Bootloader Host Application (UBHA). Compared to UBHA, mcbootflash:

- Provides no GUI.
- Can be automated.
- Can be used as a library.
- Is free and open source.
- Is written in Python instead of Java.

mcbootflash is affiliated with neither Microchip nor McDonald's.

MIT License, (C) 2022 Alexander Bessman <alexander.bessman@gmail.com>

## Installation

`pip install mcbootflash`

Once installed, mcbootflash can be run from the command line:

```bash
$ mcbootflash --port=/dev/ttyUSB0 --baudrate=460800 firmware.hex
```
