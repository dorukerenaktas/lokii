import logging

from logger.context import LoggingContext, MultiContext
from logger.formatter import MultiFormatter, PrettyExceptionFormatter


def log_config(
    logger: logging.Logger = None,
    verbose: int = logging.INFO,
    filename: str = None,
    file_verbose: int = None,
):
    """
    Use a logging configuration for a CLI application.
    This will prettify log messages for the console, and show more info in a log file.
    Parameters
    ----------
    logger : logging.Logger, default None
        The logger to configure. If None, configures the root logger
    verbose : int from 0 to 3, default 2
        Sets the output verbosity.
        Verbosity 0 shows critical errors
        Verbosity 1 shows warnings and above
        Verbosity 2 shows info and above
        Verbosity 3 and above shows debug and above
    filename : str, default None
        The file name of the log file to log to. If None, no log file is generated.
    file_verbose : int from 0 to 3, default None
        Set a different verbosity for the log file. If None, is set to `verbose`.
        This has no effect if `filename` is None.
    Returns
    -------
    A context manager that will configure the logger, and reset to the previous configuration afterwards.
    Example
    -------
    ```py
    with cli_log_config(verbose=3, filename="test.log"):
        try:
            logging.debug("A debug message")
            logging.info("An info message")
            logging.warning("A warning message")
            logging.error("An error message")
            raise ValueError("A critical message from an exception")
        except Exception as exc:
            logging.critical(str(exc), exc_info=True)
    ```
    will print (with color):
    ```txt
    DEBUG | A debug message
    An info message
    WARN  | A warning message
    ERROR | An error message
    FATAL | A critical message from an exception
        Traceback (most recent call last):
            /home/eb/projects/py-scratch/color-log.py  <module>  288: raise ValueError("A critical message from an exception")
        ValueError: A critical message from an exception
    ```
    and log:
    ```txt
    DEBUG:2022-04-03 15:22:23,528:root:A debug message
    INFO:2022-04-03 15:22:23,528:root:An info message
    WARNING:2022-04-03 15:22:23,528:root:A warning message
    ERROR:2022-04-03 15:22:23,528:root:An error message
    CRITICAL:2022-04-03 15:22:23,528:root:A critical message from an exception
        Traceback (most recent call last):
            /home/eb/projects/py-scratch/color-log.py  <module>  317: raise ValueError("A critical message from an exception")
        ValueError: A critical message from an exception
    ```
    """

    if file_verbose is None:
        file_verbose = verbose

    console_level = verbose
    file_level = file_verbose

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(MultiFormatter())
    console_handler.setLevel(console_level)

    contexts = [
        LoggingContext(logger=logger, level=min(console_level, file_level)),
        LoggingContext(logger=logger, handler=console_handler, close=False),
    ]

    if filename:
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(
            PrettyExceptionFormatter(
                "%(levelname)s:%(asctime)s:%(name)s:%(message)s", color=False
            )
        )
        file_handler.setLevel(file_level)
        contexts.append(LoggingContext(logger=logger, handler=file_handler))

    return MultiContext(*contexts)


if __name__ == "__main__":

    with log_config(verbose=logging.DEBUG, filename="test.log"):
        try:
            logging.debug("A debug message")
            logging.info("An info message")
            logging.warning("A warning message")
            logging.error("An error message")
            raise ValueError("A critical message from an exception")
        except Exception as exc:
            logging.critical(str(exc), exc_info=True)
