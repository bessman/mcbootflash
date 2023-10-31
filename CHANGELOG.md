v7.0.5
======

Documentation and maintenance release.

Documentation
-------------
- Update developer guide.

Maintenance
--------------
- Use bincopy for alignment of first and final chunks in each segment.
- Use __version__ string in sphinx conf.py.
- Narrow mypy import ignores.
- Update readthedocs python to 3.11.
- Use python3.12 instead of python3.12-dev in github-actions.

v7.0.4
======

Bug fixes
---------
- Ensure all write commands are aligned with write_size (fix #21).

v7.0.3
======

Bug fixes
---------
- The final two words of the program memory range were not written (fix #19).

v7.0.0
======

API changes
-----------
- get_response removed from public API.

Bug fixes
---------
- Don't checksum if bootloader doesn't support it (fix #16).

Misc
----
- HEX file parser changed from intelhex to bincopy.
- Improved error handling and debug logging.

v6.1.0
======

API changes
-----------
- Added function mcbootflash.protocol.get_response to read response packets from serial
  in a more robust way.
- Packet.from_serial is deprecated in favor of get_response.

Bug fixes
---------
- Fixed an off-by-one error which skipped the final word within program memory range.
- Added a workaround for a bug in the bootloader where checksum calculation would fail
  close to the upper end of program memory range (fix #13).

6.0.0

Dependency changes:
- `progressbar2` is now optional (fix #11).

API changes:
- The signature of mcbootflash.Bootloader.flash has changed. The `quiet` option is
  removed, and a new `progress_callback` option is added.

CLI changes:
- Added `--version` option to display mcbootflash version string.
- If `progressbar2` is not installed, the script falls back on displaying the progress
  as just a percentage.

Bug fixes:
- All data within program memory range is now flashed. Previously, data which was part
  of a contiguous block of data was ignored if any part of the block did not fit within
  the program memory range (fix #9).

5.1.1

Bug fixes:
- Increase timeout during flash erase (#6)

5.1.0

Misc
- Re-add some logging messages that were removed by mistake
- Fix some minor docstring mistakes
- Improve error message when receiving unexpected data
- Add build status badge

5.0.0

API changes:
- Simplify exceptions; Rename McbootflashException to
  BootloaderError and remove all derived exceptions except
  those that directly correspond to an error code.
- Simplify protocol names (modules are not namespaces).
- Rename BootloaderConnection to Bootloader and reduce code
  duplication.

Misc:
- Use pytest-reserial for testing.

4.1.1

Bug fixes:
- Fix final chunk not being written in certain situations.

Misc:
- Minor changes to console output.

4.1.0
Documentation
- Added documentation.
- Added readthedocs.

Misc:
- Added codacy badges.

4.0.0
API changes:
- BootloaderConnection.flash will always raise an exception if flashing did not succeed.
- 'quiet' is now a parameter of BootloaderConnection.flash instead of BootloaderConnection itself.


3.0.0
Features:
- By default, a progress bar is now shown while flashing. Suppress with --quiet flag.
- Command line arguments can now be overriden by applications using mcbootflash as a library. See the get_parser function for more information.

API changes:
- flash.py -> flashing.py
- BootResponseCode --> BootResponse
- FLASH_UNLOCK_KEY removed from API.
- BootloaderConnection.{quiet, hexfile} removed from API.
- BootloaderConnection.erase_flash added to API.
- Exceptions have changed significantly. See error.py for more information.

Under the hood:
- Major testing overhaul: Tests now use recorded serial traffic to verify behavior.
- Switch to flit build system.
- Enforce alphabetically sorted imports with isort.
- Enable docstring linting.
- Application code now lives in src/
- Lots of changes to logging messages.


2.0.0
Features:
- Public interface available directly via __init__.py.
- Add ChecksumPacket class.
- Add reset command.
- Improve CLI help message.
- Improve package metadata.
- Reworked exceptions to more closely match those thrown by the bootloader.

Bug fixes:
- Off-by-one error when firmware uses all available space.

Under the hood:
- Add tests.
- Add linters.
- Add CI via Github Actions.

