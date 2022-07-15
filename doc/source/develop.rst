Developer's overview
====================

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
  - pycodestyle (E203 disabled because it conflicts with black)
  - pydocstyle
  - pyflakes
  - pylint (W1203 disabled because f-strings are nice)
  - mypy (strict)

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

Tests should be representative of real-world scenarios. For this reason, tests
should mimic user actions to the greatest extent possible. Tests should
interface with the program like a user would interface with the program. Every
test should model an action the user might take, or a situation the user might
face. If you find it difficult to write tests that exercise the entire codebase
under these constraints, consider if the hard-to-hit lines are really necessary
for the program to do its job.

Recording serial traffic
^^^^^^^^^^^^^^^^^^^^^^^^

In order to test mcbootflash's behavior in isolation, i.e. without a connected
device running an appropriate bootloader, serial traffic is first recorded with
a real device. Then, during tests the recorded traffic is replayed using a
mocked serial port. A test passes if the bits written to the mocked port match
the recorded traffic exactly.

Since the ability to record serial traffic is not part of mcbootflash's normal
functionality, it is maintained as a small patch in the `record` branch. To
record serial traffic, do the following:

    1. Rebase the `record` branch on top of your working branch.
    2. Modify your test by running `.dump_log(<path_to_log.json>)` on the
       BootloaderConnection instance before finishing the test.
    3. Run the test.
    4. The recorded traffic can now be found in the `<path_to_log.json>` file.
       Place this file in the directory test/testcases/<your_test>/, where
       <your_test> is either a new test if you're adding new functionality, or
       an existing test if you are changing existing functionality.

A note on test coverage
^^^^^^^^^^^^^^^^^^^^^^^

  "If a line of code is important enough to write, it is important enough to test."

While this rule is not applicable to every piece of software out there,
mcbootflash is small and simple enough that the rule can be applied. This
project therefore aims for 100% test coverage.

100% test coverage is not a goal unto itself. Tests should never be written for
the sole purpose of increasing coverage. 100% test coverage should happen as a
side-effect of good tests.
