.. _cli:

Command-line interface
======================

Mcbootflash provides a minimal CLI script, which can be accessed via the `mcbootflash` command:

.. code-block:: console

    $ mcbootflash --help
    usage: mcbootflash [-h] -p PORT -b BAUDRATE [-t TIMEOUT] [-v] [-q] file

    Flash firmware over serial connection to a device running Microchip's 16-bit
    bootloader.

    positional arguments:
        file                  An Intel HEX file containing application firmware.

    options:
        -h, --help            show this help message and exit
        -p PORT, --port PORT  Serial port connected to the device you want to flash.
	-b BAUDRATE, --baudrate BAUDRATE
		              Symbol rate of device's serial bus.
	-t TIMEOUT, --timeout TIMEOUT
                              Try to read data from the bus for this many seconds
                              before giving up.
	-v, --verbose         Print debug messages.
	-q, --quiet           Suppress output.
            --version         Print version string.


Example usage
-------------

.. code-block:: console

    $ mcbootflash --port /dev/ttyUSB0 --baudrate 460800 firmware.hex
    Connecting to bootloader...
    Connected
    Flashing firmware.hex
    Existing application detected, erasing...
    No application detected; flash erase successful
    100%  88.7 KiB |########################################| Elapsed Time: 0:00:05
    Self verify OK


Creating application-specific scripts
-------------------------------------

The CLI script provided by mcbootflash can be used by other application to
easily create their own flashing scripts:

.. code-block:: python

    # myawesomeproject.py
    import argparse
    import mcbootflash

    def my_flash_script():
        parser = mcbootflash.get_parser()
	parser.description = "Flash firmware to my awesome project!"
	parser.add_argument("-b", "--baudrate", default=460800, help=argparse.SUPPRESS)
	mcbootflash.flash(parser.parse_args())


In this example, the script's description is changed to match the new
application, and the `baudrate` argument is given a default value of 460800
symbols / second. Additionally, the `baudrate` argument is removed from the
help text, since users of `My awesome project` are unlikely to want to change
it.

The `my_flash_script` function can now be registered as a script entry-point in
the project's build system. For example, using a PEP621-compliant build system::

    # pyproject.toml
    ...
    [project.scripts]
    awesomeproject = "myawesomeproject:my_flash_scipt"

The new script can now be run as:

.. code-block:: console

    $ awesomeproject --help
    usage: awesomeproject [-h] -p PORT [-t TIMEOUT] [-v] [-q] file

    Flash firmware to my awesome project!

    positional arguments:
        file                  An Intel HEX file containing application firmware.

    options:
        -h, --help            show this help message and exit
        -p PORT, --port PORT  Serial port connected to the device you want to flash.
	-t TIMEOUT, --timeout TIMEOUT
                              Try to read data from the bus for this many seconds
                              before giving up.
	-v, --verbose         Print debug messages.
	-q, --quiet           Suppress output.

When creating more complex applictions, it is recommended to intead use the
:class:`~mcbootflash.connection.BootloaderConnection` object directly.
