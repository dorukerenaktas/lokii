import argparse
import logging
import sys

from lokii import Lokii
from lokii.logger.context import LoggingContext
from lokii.config import CONFIG

LOKII_ASCII = r"""
▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄▄▄▄▄
█   █   █       █   █ █ █   █   █
█   █   █   ▄   █   █▄█ █   █   █
█   █   █  █ █  █      ▄█   █   █
█   █▄▄▄█  █▄█  █     █▄█   █   █
█       █       █    ▄  █   █   █
█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄▄▄█ █▄█▄▄▄█▄▄▄█ 
"""


class Command:
    def __init__(self, argv=None) -> None:
        self.argv = argv.split() if argv else sys.argv[:]
        self.prog_name = "lokii"

    def execute(self) -> None:
        """
        Given the command-line arguments, this creates a parser appropriate
        to that command, and runs it.
        """

        formatter_class = argparse.RawDescriptionHelpFormatter
        parser = argparse.ArgumentParser(
            prog=self.prog_name,
            description="%s\n%s version %s"
            % (LOKII_ASCII, self.prog_name, CONFIG.version),
            formatter_class=formatter_class,
        )

        parser.add_argument(
            "--version", action="version", version="%(prog)s " + CONFIG.version
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
            "-e",
            "--export",
            action="store_true",
            help="execute group export modules",
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
                _lokii = Lokii(arguments.source_folder)
                _lokii.generate(arguments.export, arguments.purge)
            except Exception as err:
                logging.critical(str(err), exc_info=True)


def exec_cmd(argv=None) -> None:
    command = Command(argv)
    command.execute()
