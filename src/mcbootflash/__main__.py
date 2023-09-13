"""Command-line scripts."""
from typing import List, Union

import mcbootflash


def main(args: Union[None, List[str]] = None) -> None:
    """Entry point."""
    parser = mcbootflash.get_parser()
    parser.add_argument(
        "--version",
        action="version",
        version=f"{mcbootflash.__version__}",
    )
    parsed_args = parser.parse_args(args)
    mcbootflash.flash(parsed_args)
