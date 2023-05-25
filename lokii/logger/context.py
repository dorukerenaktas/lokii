import logging

from lokii.logger.formatter import MultiFormatter


class LoggingContext:
    """
    Use a logging configuration for a CLI application.
    This will prettify log messages for the console, and show more info in a log file.
    :param logger: the logger to configure. If None, configures the root logger
    :param level:  sets the output verbosity
    :param filename:  the file name of the log file to log to. If None, no log file is generated.
    :return: a context manager that will configure the logger, and reset to the previous
    configuration afterward.
    """

    def __init__(
        self,
        logger: logging.Logger = None,
        level: int = logging.INFO,
        filename: str = None,
    ):
        self.logger = logger or logging.root
        self.level = level
        self.old_level = self.logger.level

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(MultiFormatter())
        console_handler.setLevel(self.level)
        self.handlers = [console_handler]

        if filename:
            file_handler = logging.FileHandler(filename)
            fmt = "%(levelname)s:%(asctime)s:%(name)s:%(message)s"
            file_handler.setFormatter(logging.Formatter(fmt))
            file_handler.setLevel(self.level)
            self.handlers.append(file_handler)

    def __enter__(self):
        # configure logger with given parameters
        self.logger.setLevel(self.level)
        for handler in self.handlers:
            self.logger.addHandler(handler)

    def __exit__(self, *exc_info):
        # revert back to old logger configuration
        self.logger.setLevel(self.old_level)
        for handler in self.handlers:
            self.logger.removeHandler(handler)
