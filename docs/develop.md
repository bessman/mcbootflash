# Developer's Guide

## Tl;dr

Just run `tox`. If everything passes, you're OK. If not, read on.

## Formatting and Linting

Mcbootflash uses the following tools for automatic formatting, linting, and static type
checking:

- black
- isort
- mypy
- ruff

Autoformat with `tox -e format`.

Lint and type check with `tox -e lint`.

These checks run automatically for all pull requests, and must pass before merge.

## Code style

In addition to these automatically enforced rules, the following style rules apply:

- Blank lines before and after indented code blocks (1), unless the block starts at the
  beginning of another block (2).

- Comments and docstrings are sentences; They start with capital letter and end with a
  period. Docstrings follow
  [Numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html) style (3).

- Class names are CamelCase. Underscore is not allowed except at the start of
  the name to mark the class as private. Class names should be nouns (4).

- Function names are snake_case with underscore separating words. Function
  names should be verbs or verb phrases (5).

- Variables which are local to a function scope are snake_case, same as functions.
  Variable names should be nouns or adjectives (6).

- Module-level variables and class variables are SCREAMING_SNAKE_CASE (7).

??? example "Code style example"

    ``` py
    """Spam-related things go here."""
    from __future__ import annotations

    MAX_SPAM = 5                                                     # (7)
    
    
    class Spam:                                                      # (4)
        """Spiced ham."""
    
    
    def eat_spam(spams: list[Spam]) -> int:                          # (5)
        """Eat spam and report how many spams were eaten.            # (3)
    
        Parameters
        ----------
        spams : list[Spam]
            Spam spam spam.
    
        Returns
        -------
        eaten : int
            Number of spams eaten.
        """
        eaten = 0                                                    # (6)
                                                                     # (1)
        for _ in spams:
            if eaten >= MAX_SPAM:                                    # (2)
                print("Can't eat more spam.")
                break

            print("Ate spam.")
            eaten += 1

        return eaten
    ```

Testing
-------

Mcbootflash is tested with pytest. To run the tests, use `tox -e test`.


Most of mcbootflash's functionality revolves around reading and writing data
from/to a serial bus. Testing mcbootflash therefore involves checking that
mcbootflash:

1. writes the expected bytes to the bus,
2. reads the correct number of bytes in response, and
3. processes the response data correctly.

This is accomplished by means of a pytest plugin,
[pytest-reserial](https://github.com/bessman/pytest-reserial). Serial traffic
is first recorded by running the tests against a real device running the
bootloader. Then, during tests the recorded traffic is replayed using a mocked
serial port. A test passes if the bits written to and read from the mocked
port match the recorded traffic exactly.

To create a new test, or update an old one, run
`pytest --record -k <test_name>` with a device in bootloader mode connected at
/dev/ttyUSB0 with a baudrate of 460800 (the port name and baudrate are
currently hardcoded during testing; pull requests welcome if you need them to
be dynamic).
