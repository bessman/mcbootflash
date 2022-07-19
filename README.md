# mcbootflash

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

Additionally, mcbootflash is can be used as a library by applications which
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