# Changelog

## [10.1.1-pre0] - Development

### Changed

- Turn developer's guide into CONTRIBUTING.md ([`b77fda0`](https://github.com/bessman/mcbootflash/commit/b77fda0c2857d29b6f3f5f430d62ffb51d242d5c))

## [10.1.0] - 2025-01-16

### Changed

- Workaround bootloader bug during erase ([`4203827`](https://github.com/bessman/mcbootflash/commit/420382732970a26dc6ed66bf9787c4c88f48f2f1))

### Added

- Add stand-alone executables in releases ([`26e4202`](https://github.com/bessman/mcbootflash/commit/26e420243d54a4b0c82ad802a1c9d68639633e60))

### Fixed

- Handle HEX-file not found error ([`94c76a6`](https://github.com/bessman/mcbootflash/commit/94c76a67e6fd883ff83f64771646c270d100feec))

## [10.0.0] - 2024-12-22

### Changed

- __Breaking__: Rename --verbose CLI flag to --debug ([`5116ffe`](https://github.com/bessman/mcbootflash/commit/5116ffeec3369fe024d9f1cc730ce57f6dd91232))
- __Breaking__: Raise `bincopy.Error` instead of `ValueError` in `chunked` ([`452afb5`](https://github.com/bessman/mcbootflash/commit/452afb59b8205406b70a3604214070f1c6b625e4))
- Improve CLI error handling ([`5116ffe`](https://github.com/bessman/mcbootflash/commit/5116ffeec3369fe024d9f1cc730ce57f6dd91232))
- Clarify `self_verify` docstring ([`fc8d16b`](https://github.com/bessman/mcbootflash/commit/fc8d16b2d9b6ee528edbeec7bd47a4a157c3b78b))

### Added

- Implement `read_flash` ([`908aeac`](https://github.com/bessman/mcbootflash/commit/908aeac1ff28985ac0697a44362cf8753354013b))
- Add `readback` utility function to read firmware image from flash ([`53481c2`](https://github.com/bessman/mcbootflash/commit/53481c2980d8feb0fc4459a9c025d0aa8ecf8241))
- Add support for Python 3.13 ([`a74ed75`](https://github.com/bessman/mcbootflash/commit/a74ed753406161a56fd758e0fa45193350a88120))

### Removed

- Drop support for EOL Python 3.8 ([`a74ed75`](https://github.com/bessman/mcbootflash/commit/a74ed753406161a56fd758e0fa45193350a88120))

### Fixed

- __Breaking__: Re-rename types.py to protocol.py to avoid shadowing built-in types.py ([`2a66b7b`](https://github.com/bessman/mcbootflash/commit/2a66b7b6df783b9d3b81a1592d6732c8440e767e))

## [9.0.1] - 2024-05-14

### Changed

- Make minor improvements to CLI output ([`fb17948`](https://github.com/bessman/mcbootflash/commit/fb17948310d85f30b3f7b451e02dfded53b7faa7))

### Fixed

- Update README to reflect changes made in v9.0.0 ([`e6dc42c`](https://github.com/bessman/mcbootflash/commit/e6dc42c2747dc42efb2ce03f15dc535907796f11))

## [9.0.0] - 2024-05-13

### Changed

- Disable checksumming by default in CLI, enable with `--checksum` flag ([`b685bb5`](https://github.com/bessman/mcbootflash/commit/b685bb56165805706fdc87adcba76c1285cc3416))
- Unconditionally erase before flashing with CLI ([`9a4ddc6`](https://github.com/bessman/mcbootflash/commit/9a4ddc629b1df47fe06149ceafdc3f4131a5e6e6))

### Added

- Add CLI flag `--reset` to reset device after flashing ([`e38cefb`](https://github.com/bessman/mcbootflash/commit/e38cefbfee740b46c994d678f1fd884d8caeec9c))

### Removed

- __Breaking__: Remove `.has_checksum` attribute versionof `BootAttrs` ([`b685bb5`](https://github.com/bessman/mcbootflash/commit/b685bb56165805706fdc87adcba76c1285cc3416))

### Fixed

- Fix error messages not being shown in CLI ([`c499eb9`](https://github.com/bessman/mcbootflash/commit/c499eb94f193b2910aed6c6fb62f108854ce8026))
- Fix wrong pad value in `chunked` ([`58ad227`](https://github.com/bessman/mcbootflash/commit/58ad227b9304ddea3f9c0e4acad1494901a47031))

## [8.0.2] - 2024-05-11

### Fixed

- Continue with warning on `BadAddress` during checksum ([`b8734ea`](https://github.com/bessman/mcbootflash/commit/b8734ea2d4b63a3ae005031629a1b6c73c83dd49))

## [8.0.1] - 2024-02-08

### Changed

- Bump development status trove classifier: Beta -> Stable ([`418142e`](https://github.com/bessman/mcbootflash/commit/418142e1df232219b472027a52020ffe074fab28))
- Begin argument descriptions with lowercase letter ([`103a331`](https://github.com/bessman/mcbootflash/commit/103a3313aec6fb6eb4c08ee35ecadd97055b0335))

### Fixed

- Fix `chunked` missing from API reference ([`a276764`](https://github.com/bessman/mcbootflash/commit/a276764074187cbe344fe553916f4472f410d54a))

## [8.0.0] - 2023-11-09

### Changed

- __Breaking__: Renamed `connection.py` to `flash.py` ([`3319508`](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- __Breaking__: Renamed `protocol.py` to `types.py` ([`4d73ca0`](https://github.com/bessman/mcbootflash/commit/4d73ca04d764765fedac17b68f04cea89a82e1b1))
- Renamed `file` argument to CLI to `hexfile` ([`5a0d612`](https://github.com/bessman/mcbootflash/commit/5a0d6129e53843b2d01d1f69b4cb3723500f3b2b))
- Replace sphinx with mkdocs ([`4a9e854`](https://github.com/bessman/mcbootflash/commit/4a9e85476b5986c6c25af079845b9859f80db019))
- Split tox.ini from pyproject.toml to separate file ([`08ef0ed`](https://github.com/bessman/mcbootflash/commit/08ef0ed2dd8d81a03246f4ca832c426573e514fe))
- Use `from __future__ import annotations` ([`04ed4f9`](https://github.com/bessman/mcbootflash/commit/04ed4f973ef0f928c05131f0894725ad8730657d))
- Improve CI time by not installing in environments that don't need it ([`6d381ee`](https://github.com/bessman/mcbootflash/commit/6d381eefa77fc731bf5238c345dc18bc21bf6962))

### Added

- Add `BootAttrs` dataclass for holding bootloader attributes ([`afcfa08`](https://github.com/bessman/mcbootflash/commit/afcfa08853b304aaf92fa344195696760db95f29))
- Add `Chunk` protocol for data which is to be written to flash ([`afcfa08`](https://github.com/bessman/mcbootflash/commit/afcfa08853b304aaf92fa344195696760db95f29))
- Add `Connection` protocol for objects which provide a connection to a device in bootloader mode ([`afcfa08`](https://github.com/bessman/mcbootflash/commit/afcfa08853b304aaf92fa344195696760db95f29))
- Add `get_boot_attrs` function to read bootloader attributes ([`3319508`](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add `chunked` to load and split HEX file into aligend chunks ([`afcfa08`](https://github.com/bessman/mcbootflash/commit/afcfa08853b304aaf92fa344195696760db95f29))
- Add `erase_flash` to erase program memory range ([`3319508`](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add `write_flash` to write firmware chunks to flash ([`3319508`](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add `checksum` to compare local and remote data ([`3319508`](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add `self_verify` to detect installed application on device ([`3319508`](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add `reset` to reset device ([`3319508`](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- Add github pages ([`f02b7c6`](https://github.com/bessman/mcbootflash/commit/f02b7c613e4dd8f2410a69e2b785e81b883ee92c))
- Start using ruff for linting ([`82e1a95`](https://github.com/bessman/mcbootflash/commit/82e1a9539780edfb5eb9ef0cef28a202a74ddd4b))

### Removed

- __Breaking__: Remove `flashing.py` ([`969d110`](https://github.com/bessman/mcbootflash/commit/969d11063db184fe0b84fbf10ecd7575df393b72))
- __Breaking__: Remove `mcbootflash.get_parser` ([`969d110`](https://github.com/bessman/mcbootflash/commit/969d11063db184fe0b84fbf10ecd7575df393b72))
- __Breaking__: Remove `mcbootflash.flash` ([`969d110`](https://github.com/bessman/mcbootflash/commit/969d11063db184fe0b84fbf10ecd7575df393b72))
- __Breaking__: Remove `mcbootflash.Bootloader` ([`3319508`](https://github.com/bessman/mcbootflash/commit/3319508ddd9b0935b8823f551587e224a2d38dcb))
- __Breaking__: Remove `mcbootflash.protocol.Packet.from_serial` ([`f5cb75c`](https://github.com/bessman/mcbootflash/commit/f5cb75c114fc6a25823d909440683d12d8133505))
- Stop using prospector for linting ([`eed8b6a`](https://github.com/bessman/mcbootflash/commit/eed8b6a4c155bab38a1eccd132d8d87bbb04c8a4))
- Stop using readthedocs ([`f4a128d`](https://github.com/bessman/mcbootflash/commit/f4a128ded9c156cbd6817ee77965f7bf64cbf803))

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

[10.1.1-pre0]: https://github.com/bessman/mcbootflash/releases/tag/10.1.1-pre0
[10.1.0]: https://github.com/bessman/mcbootflash/releases/tag/10.1.0
[10.0.0]: https://github.com/bessman/mcbootflash/releases/tag/10.0.0
[9.0.1]: https://github.com/bessman/mcbootflash/releases/tag/9.0.1
[9.0.0]: https://github.com/bessman/mcbootflash/releases/tag/9.0.0
[8.0.2]: https://github.com/bessman/mcbootflash/releases/tag/8.0.2
[8.0.1]: https://github.com/bessman/mcbootflash/releases/tag/8.0.1
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
