# Changelog

## [7.0.5] - 2023-10-31

_Maintanence release._

### Changed

- Update developer guide
- Use bincopy for alignment of first and final chunks in each segment
- Use `__version__` string in sphinx `conf.py`
- Narrow mypy import ignores
- Update readthedocs python to 3.11
- Use python3.12 instead of python3.12-dev in github-actions

## [7.0.4] - 2023-10-07

### Fixed

- Align all write commands with `write_size` ([#21](https://github.com/bessman/mcbootflash/issues/21))

## [7.0.3] - 2023-09-26

### Fixed

- Write the final two words of the program memory range ([#19](https://github.com/bessman/mcbootflash/issues/19))

## [7.0.0] - 2023-09-23

### Changed

- Change HEX file parser from intelhex to bincopy
- Improve error handling and debug logging

### Removed

- __Breaking:__ Remove `get_response`

### Fixed

- Don't checksum if bootloader doesn't support it ([#16](https://github.com/bessman/mcbootflash/issues/16))

## [6.1.0] - 2023-09-15

### Changed

- Deprecate `Packet.from_serial` in favor of `get_response`

### Added

- Add function `mcbootflash.protocol.get_response`

### Fixed

- Fix an off-by-one error which skipped the final word within program memory range
- Skip checksum calculation close to the upper end of program memory range ([#13](https://github.com/bessman/mcbootflash/issues/13))

## [6.0.0] - 2023-09-13

### Changed

- Make `progressbar2` optional ([#11](https://github.com/bessman/mcbootflash/issues/11))
- Display progress as a percentage value if `progressbar2` is not installed

### Added

- Add parameter `progress_callback` to `mcbootflash.Bootloader.flash`
- Add `--version` option to display mcbootflash version string

### Removed

- __Breaking:__ Remove parameter `quiet` from `mcbootflash.Bootloader.flash`

### Fixed

- Flash all data within program memory range ([#9](https://github.com/bessman/mcbootflash/issues/9))

## [5.1.1] - 2023-04-26

### Fixed

- Increase timeout during flash erase ([#6](https://github.com/bessman/mcbootflash/issues/6))

## [5.1.0] - 2023-01-13

### Changed

- Fix some minor docstring mistakes
- Improve error message when receiving unexpected data

### Added

- Re-add some logging messages that were removed by mistake
- Add build status badge

## [5.0.0] - 2022-11-29

### Changed

- __Breaking:__ Rename McbootflashException to BootloaderError
- __Breaking:__ Simplify protocol names (modules are not namespaces)
- __Breaking:__ Rename BootloaderConnection to Bootloader
- Use pytest-reserial for testing

### Removed

- __Breaking:__ Remove several custom exceptions

## 4.1.1 - 2022-09-17

### Fixed

- Fix final chunk not being written in certain situations
- Fix minor errors in console output

## [4.1.0] - 2022-07-19

### Added

- Add documentation
- Add readthedocs
- Add codacy badges

## 4.0.0 - 2022-07-12

### Changed

- __Breaking:__ Move `quiet` parameter to `BootloaderConnection.flash`
- Raise exception from BootloaderConnection.flash if flashing did not succeed

## [3.0.0] - 2022-07-11

### Changed

- __Breaking:__ Rename `flash.py` -> `flashing.py`
- __Breaking:__ Rename `BootResponseCode` -> `BootResponse`
- __Breaking:__ Refactor exceptions
- Use recorded serial traffic to verify behavior
- Move application code to src/
- Switch to flit build system
- Enable docstring linting
- Enforce alphabetically sorted imports with isort
- Change lots of logging messages

### Added

- Add progress bar while flashing. Suppress with `--quiet` flag
- Allow overriding CLI arguments
- Add `BootloaderConnection.erase_flash`

### Removed

- __Breaking:__ Remove `FLASH_UNLOCK_KEY`
- __Breaking:__ Remove `BootloaderConnection.{quiet, hexfile}`

## [2.0.0] - 2022-06-12

### Changed

- Improve CLI help message
- Improve package metadata
- Reworke exceptions to more closely match those thrown by the bootloader

### Added

- Add public interface to `__init__.py`
- Add `ChecksumPacket` class
- Add `reset` command
- Add tests
- Add linters
- Add CI via Github Actions

### Fixes

- Fix off-by-one error when firmware uses all available space

## [1.0.0] - 2022-05-27

_Initial release._

[7.0.5]: https://github.com/bessman/mcbootflash/releases/tag/v7.0.5
[7.0.4]: https://github.com/bessman/mcbootflash/releases/tag/v7.0.4
[7.0.3]: https://github.com/bessman/mcbootflash/releases/tag/v7.0.3
[7.0.0]: https://github.com/bessman/mcbootflash/releases/tag/v7.0.0
[6.1.0]: https://github.com/bessman/mcbootflash/releases/tag/v6.1.0
[6.0.0]: https://github.com/bessman/mcbootflash/releases/tag/v6.0.0
[5.1.1]: https://github.com/bessman/mcbootflash/releases/tag/v5.1.1
[5.1.0]: https://github.com/bessman/mcbootflash/releases/tag/v5.1.0
[5.0.0]: https://github.com/bessman/mcbootflash/releases/tag/v5.0.0
[4.1.0]: https://github.com/bessman/mcbootflash/releases/tag/4.1.0
[3.0.0]: https://github.com/bessman/mcbootflash/releases/tag/3.0.0
[2.0.0]: https://github.com/bessman/mcbootflash/releases/tag/2.0.0
[1.0.0]: https://github.com/bessman/mcbootflash/releases/tag/1.0.0
