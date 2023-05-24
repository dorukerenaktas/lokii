import logging
from textwrap import indent

from .color import default_formats


class PrettyExceptionFormatter(logging.Formatter):
    """Uses pretty-traceback to format exceptions"""

    def __init__(self, *args, color=True, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.color = color

    def format(self, record: logging.LogRecord):
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        s = self.formatMessage(record)

        if record.exc_info:
            # Don't assign to exc_text here, since we don't want to inject color all the time
            if s[-1:] != "\n":
                s += "\n"
            # Add indent to indicate the traceback is part of the previous message
            text = indent(self.formatException(record.exc_info), " " * 4)
            s += text

        return s


class MultiFormatter(PrettyExceptionFormatter):
    """Format log messages differently for each log level"""

    def __init__(self, formats: dict[int, str] = None, **kwargs):
        base_format = kwargs.pop("fmt", None)
        super().__init__(base_format, **kwargs)

        formats = formats or default_formats

        self.formatters = {
            level: PrettyExceptionFormatter(fmt, **kwargs)
            for level, fmt in formats.items()
        }

    def format(self, record: logging.LogRecord):
        formatter = self.formatters.get(record.levelno)

        if formatter is None:
            return super().format(record)

        return formatter.format(record)
