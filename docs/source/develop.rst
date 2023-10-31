Developer's overview
====================

Tl;dr
-----

Just run :code:`tox`. If everything passes, you're OK. If not, read on.

Code style
----------

The mcbootflash authors strive to find as many bugs as possible during the
development stage. For that reason, the following tools are used to enforce
best-practice conventions (default settings unless otherwise noted):

- black
- isort
- prospector (strictness: veryhigh), which runs the following tools in turn:

  - bandit
  - dodgy
  - mccabe (max-complexity 5)
  - pycodestyle (E203 disabled [#E203]_)
  - pydocstyle (numpy style)
  - pyflakes
  - pylint (W1203 disabled [#W1203]_)
  - mypy (strict)

.. [#E203] pycodestyle E203 conflicts with black, see
           https://github.com/PyCQA/pycodestyle/issues/373.
.. [#W1203] See https://github.com/pylint-dev/pylint/issues/2354. Tl;dr:
            F-strings in log messages negatively impact performance compared
            to %s-style formatting. However, the impact is very small. Because
            f-strings are more readable, mcbootflash accepts the performance
            hit.

In addition to these automatically enforced rules, the following conventions are
used:

- Blank lines before and after code blocks started by a statement (if, while,
  return, …) (1), unless the block is only a single line (2), or comes at the
  beginning or end of another statement (3).

- Comments and docstrings starts with capital letter and ends with a period,
  that is, just as sentences (4).

- Class names are CamelCase. Underscore is not allowed except at the start of
  the name to mark the class as private (5).

- Function names are snake_case with underscore separating words. Function
  names should be verbs or verb phrases (6).

- Instance variables and variables which are local to a function scope are
  snake_case, same as functions (7).

- Module-level variables and class variables are SCREAMING_SNAKE_CASE (8).

.. code-block:: python

    from os import getcwd 
    from os import path

    FUM = 0                                            # (8)


    class Foo:                                         # (5)
    """This is a doc string."""                        # (4)

        BAR = 1                                        # (8)

        def __init__(self, fies: List = []):           # (7)
            self.fies = fies


    def eat_ham(bars: int, goo: None = None) -> List:  # (6)
        """This is a doc string."""                    # (4)

        fies = []
        ham = path.join(getcwd(), '..')
                                                       # (1)
        for bar in bars:
            if len(bar) == 1):                         # (3)
                fies.append(ham + 2 * bar)
                                                       # (1)
        # This is a comment.                           # (4)
        if fum in None:
            fum = 5
        else:
            fum += 1
                                                       # (1)
        ham *= fum
        return ham                                     # (2)

Testing
-------

When testing software, what should be tested is *behavior* rather than
*implementation*. In other words, test *what* the software does, not *how* it
does it. In the case of mcbootflash, behavior is the bits that are written to
the serial port, as well as what is done with the bits read from the same.

By testing behavior rather than implementation, we remove the need to update
tests whenever the code changes slightly. Tests only require updating when the
program's behavior changes, i.e. the data it writes to the serial bus in
response to any given command. If a test fails when you didn't intend to
change the program's behavior, you broke something.

Recording serial traffic
^^^^^^^^^^^^^^^^^^^^^^^^

In order to test mcbootflash's behavior in isolation, i.e. without a connected
device running an appropriate bootloader, serial traffic is first recorded with
a real device. Then, during tests the recorded traffic is replayed using a
mocked serial port. A test passes if the bits written to and read from the
mocked port match the recorded traffic exactly.

A pytest plugin, pytest-reserial_, is used to record and replay serial traffic.
To create a new test, or update an old one when intentionally changing
mcbootflash's behavior, run :code:`pytest --record -k <test_name>` with a device
running the bootloader connected at /dev/ttyUSB0 with a baudrate of 460800
(this port name and baudrate are currently hardcoded during testing; pull
requests welcome if you need them to be dynamic).

.. _pytest-reserial: https://github.com/bessman/pytest-reserial
