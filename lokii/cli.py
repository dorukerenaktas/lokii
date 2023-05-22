import argparse
import logging
import sys

from pathlib import Path
from typing import Optional

from lokii import Lokii
from lokii.logger import log_config
from lokii.config import VERSION

LOKII_ASCII = r"""
 __         ______     __  __     __     __    
/\ \       /\  __ \   /\ \/ /    /\ \   /\ \   
\ \ \____  \ \ \/\ \  \ \  _"-.  \ \ \  \ \ \  
 \ \_____\  \ \_____\  \ \_\ \_\  \ \_\  \ \_\ 
  \/_____/   \/_____/   \/_/\/_/   \/_/   \/_/ 
"""
LOKII_EPILOG = f""""""


class Command:
    def __init__(self, argv: Optional[str] = None) -> None:
        self.argv = argv or sys.argv[:]
        self.prog_name = Path(self.argv[0]).name

    def execute(self) -> None:
        """
        Given the command-line arguments, this creates a parser appropriate
        to that command, and runs it.
        """

        formatter_class = argparse.RawDescriptionHelpFormatter
        parser = argparse.ArgumentParser(
            prog=self.prog_name,
            description=f"{LOKII_ASCII}\n{self.prog_name} version {VERSION}",
            epilog=LOKII_EPILOG,
            formatter_class=formatter_class,
        )

        parser.add_argument(
            "--version", action="version", version=f"%(prog)s {VERSION}"
        )

        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="set logging level to DEBUG that shows all events",
        )

        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="set logging level to CRITICAL that shows only blocking events",
        )

        parser.add_argument(
            "-f",
            "--source-folder",
            metavar="PATH",
            default=".",
            type=str,
            help="generate the specified number of outputs",
        )

        parser.add_argument(
            "-o",
            "--out-folder",
            metavar="PATH",
            default="./data",
            type=str,
            help="redirect output to a file",
        )

        parser.add_argument(
            "--seed",
            metavar="SEED",
            type=int,
            help="specify a seed for the random generator so "
            "that results are repeatable. Also compatible "
            "with 'repeat' option",
        )

        parser.add_argument(
            "fake",
            action="store",
            nargs="?",
            help="name of the fake to generate output for " "(e.g. profile)",
        )

        parser.add_argument(
            "fake_args",
            metavar="fake argument",
            action="store",
            nargs="*",
            help="optional arguments to pass to the fake "
            "(e.g. the profile fake takes an optional "
            "list of comma separated field names as the "
            "first argument)",
        )

        arguments = parser.parse_args(self.argv[1:])

        verbose = logging.INFO
        if arguments.verbose:
            verbose = logging.DEBUG
        if arguments.quiet:
            verbose = logging.CRITICAL

        with log_config(verbose=verbose):
            try:
                logging.info(LOKII_ASCII)
                lokii_gen = Lokii(arguments.source_folder, arguments.out_folder)
                lokii_gen.generate()
            except Exception as err:
                logging.critical(str(err), exc_info=True)


def execute_from_command_line(argv: Optional[str] = None) -> None:
    """A simple method that runs a Command."""
    command = Command(argv)
    command.execute()


if __name__ == "__main__":
    execute_from_command_line()
