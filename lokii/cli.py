import argparse
import logging
import sys

from pathlib import Path
from typing import Optional

from lokii import Lokii
from lokii.logger.context import LoggingContext
from lokii.config import CONFIG

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
        self.argv = argv.split() if argv else sys.argv[:]
        self.prog_name = Path(self.argv[0]).name

    def execute(self) -> None:
        """
        Given the command-line arguments, this creates a parser appropriate
        to that command, and runs it.
        """

        formatter_class = argparse.RawDescriptionHelpFormatter
        parser = argparse.ArgumentParser(
            prog=self.prog_name,
            description=f"{LOKII_ASCII}\n{self.prog_name} version {CONFIG.version}",
            epilog=LOKII_EPILOG,
            formatter_class=formatter_class,
        )

        parser.add_argument(
            "--version", action="version", version=f"%(prog)s {CONFIG.version}"
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
            "-l",
            "--log-file",
            action="store",
            help="set the file path where the log file will be created",
        )

        parser.add_argument(
            "-f",
            "--source-folder",
            action="store",
            metavar="PATH",
            default=".",
            type=str,
            help="generate the specified number of outputs",
        )

        parser.add_argument(
            "-o",
            "--out-folder",
            action="store",
            metavar="PATH",
            default="./data",
            type=str,
            help="redirect output to a file",
        )

        parser.add_argument(
            "-p",
            "--purge",
            action="store_true",
            help="purge cache database after generation",
        )

        arguments = parser.parse_args(self.argv[1:])

        verbose = logging.INFO
        if arguments.verbose:
            verbose = logging.DEBUG
        if arguments.quiet:
            verbose = logging.ERROR

        with LoggingContext(level=verbose, filename=arguments.log_file):
            try:
                print(LOKII_ASCII)
                lokii_gen = Lokii(arguments.source_folder, arguments.out_folder)
                lokii_gen.generate(arguments.purge)
            except Exception as err:
                logging.critical(str(err), exc_info=True)


def exec_cmd(argv: Optional[str] = None) -> None:
    """A simple method that runs a Command."""
    command = Command(argv)
    command.execute()
