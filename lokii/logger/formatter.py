from logging import Formatter, LogRecord

from lokii.logger.color import default_formats


class MultiFormatter(Formatter):
    """Format log messages differently for each log level"""

    def __init__(self, formats: dict[int, str] = None, **kwargs):
        base_format = kwargs.pop("fmt", None)
        super(MultiFormatter, self).__init__(base_format, **kwargs)
        fmts = formats or default_formats
        self.formatters = {lvl: Formatter(fmt, **kwargs) for lvl, fmt in fmts.items()}

    def format(self, r: LogRecord):
        fmt = self.formatters.get(r.levelno)
        return super(MultiFormatter, self).format(r) if fmt is None else fmt.format(r)
