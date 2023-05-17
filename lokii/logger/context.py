import logging


class LoggingContext:
    def __init__(
        self,
        logger: logging.Logger = None,
        level: int = None,
        handler: logging.Handler = None,
        close: bool = True,
    ):
        self.logger = logger or logging.root
        self.level = level
        self.handler = handler
        self.close = close

    def __enter__(self):
        if self.level is not None:
            self.old_level = self.logger.level
            self.logger.setLevel(self.level)

        if self.handler:
            self.logger.addHandler(self.handler)

    def __exit__(self, *exc_info):
        if self.level is not None:
            self.logger.setLevel(self.old_level)

        if self.handler:
            self.logger.removeHandler(self.handler)

        if self.handler and self.close:
            self.handler.close()


class MultiContext:
    """Can be used to dynamically combine context managers"""

    def __init__(self, *contexts) -> None:
        self.contexts = contexts

    def __enter__(self):
        return tuple(ctx.__enter__() for ctx in self.contexts)

    def __exit__(self, *exc_info):
        for ctx in self.contexts:
            ctx.__exit__(*exc_info)
