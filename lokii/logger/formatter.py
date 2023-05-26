from logging import Formatter, LogRecord

from lokii.logger.color import default_formats


class MultiFormatter(Formatter):
    """Format log messages differently for each log level"""

    def __init__(self, formats: dict[int, str] = None, **kwargs):
        base_format = kwargs.pop("fmt", None)
        super().__init__(base_format, **kwargs)
        fmts = formats or default_formats
        self.formatters = {lvl: Formatter(fmt, **kwargs) for lvl, fmt in fmts.items()}

    def format(self, record: LogRecord):
        formatter = self.formatters.get(record.levelno)
        return super().format(record) if formatter is None else formatter.format(record)
