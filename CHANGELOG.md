# Changelog

## [8.0.1] - Development

## [8.0.0] - 2023-11-09

### Changed

- __Breaking__: Renamed `connection.py` to `flash.py` ([3319508](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- __Breaking__: Renamed `protocol.py` to `types.py` ([4d73ca0](https://github.com/bessman/mcbootflash/commit/4d73ca04d764765fedac17b68f04cea89a82e1b1))
- Renamed `file` argument to CLI to `hexfile` ([5a0d612](https://github.com/bessman/mcbootflash/commit/5a0d6129e53843b2d01d1f69b4cb3723500f3b2b))
- Replace sphinx with mkdocs ([4a9e854](https://github.com/bessman/mcbootflash/commit/4a9e85476b5986c6c25af079845b9859f80db019))
- Split tox.ini from pyproject.toml to separate file ([08ef0ed](https://github.com/bessman/mcbootflash/commit/08ef0ed2dd8d81a03246f4ca832c426573e514fe))
- Use `from __future__ import annotations` ([04ed4f9](https://github.com/bessman/mcbootflash/commit/04ed4f973ef0f928c05131f0894725ad8730657d))
- Improve CI time by not installing in environments that don't need it ([6d381ee](https://github.com/bessman/mcbootflash/commit/6d381eefa77fc731bf5238c345dc18bc21bf6962))

### Added

- Add `BootAttrs` dataclass for holding bootloader attributes ([afcfa08](https://github.com/bessman/mcbootflash/commit/afcfa08853b304aaf92fa344195696760db95f29))
- Add `Chunk` protocol for data which is to be written to flash ([afcfa08](https://github.com/bessman/mcbootflash/commit/afcfa08853b304aaf92fa344195696760db95f29))
- Add `Connection` protocol for objects which provide a connection to a device in bootloader mode ([afcfa08](https://github.com/bessman/mcbootflash/commit/afcfa08853b304aaf92fa344195696760db95f29))
- Add `get_boot_attrs` function to read bootloader attributes ([3319508](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add `chunked` to load and split HEX file into aligend chunks ([afcfa08](https://github.com/bessman/mcbootflash/commit/afcfa08853b304aaf92fa344195696760db95f29))
- Add `erase_flash` to erase program memory range ([3319508](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add `write_flash` to write firmware chunks to flash ([3319508](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add `checksum` to compare local and remote data ([3319508](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add `self_verify` to detect installed application on device ([3319508](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add `reset` to reset device ([3319508](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add github pages ([f02b7c6](https://github.com/bessman/mcbootflash/commit/f02b7c613e4dd8f2410a69e2b785e81b883ee92c))
- Start using ruff for linting ([82e1a95](https://github.com/bessman/mcbootflash/commit/82e1a9539780edfb5eb9ef0cef28a202a74ddd4b))

### Removed

- __Breaking__: Remove `flashing.py` ([969d110](https://github.com/bessman/mcbootflash/commit/969d11063db184fe0b84fbf10ecd7575df393b72))
- __Breaking__: Remove `mcbootflash.get_parser` ([969d110](https://github.com/bessman/mcbootflash/commit/969d11063db184fe0b84fbf10ecd7575df393b72))
- __Breaking__: Remove `mcbootflash.flash` ([969d110](https://github.com/bessman/mcbootflash/commit/969d11063db184fe0b84fbf10ecd7575df393b72))
- __Breaking__: Remove `mcbootflash.Bootloader` ([3319508](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- __Breaking__: Remove `mcbootflash.protocol.Packet.from_serial` ([f5cb75c](https://github.com/bessman/mcbootflash/commit/f5cb75c114fc6a25823d909440683d12d8133505))
- Stop using prospector for linting ([eed8b6a](https://github.com/bessman/mcbootflash/commit/eed8b6a4c155bab38a1eccd132d8d87bbb04c8a4))
- Stop using readthedocs ([f4a128d](https://github.com/bessman/mcbootflash/commit/f4a128ded9c156cbd6817ee77965f7bf64cbf803))

## [7.0.6] - 2023-11-01

### Changed

- Reformat changelog per [Common Changelog](https://common-changelog.org/) style ([`6447957`](https://github.com/bessman/mcbootflash/commit/6447957005efc681646df59536c68dac3d24619d))

### Fixed

- Actually use bincopy for alignment ([#25](https://github.com/bessman/mcbootflash/issues/25))([`a668b9d`](https://github.com/bessman/mcbootflash/commit/a668b9d02394e255d28eb68c36bc6a226191d968))

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

[8.0.0]: https://github.com/bessman/mcbootflash/releases/tag/v8.0.0
[7.0.6]: https://github.com/bessman/mcbootflash/releases/tag/v7.0.6
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
