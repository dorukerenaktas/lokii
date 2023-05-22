import time


class PerfTimerContext:
    """
    Simple perf_counter implementation that tracks elapsed time in context.
    """

    def __enter__(self):
        self.time = time.perf_counter()
        return self

    def __exit__(self, _, __, ___):
        self.time = time.perf_counter() - self.time

    def __str__(self):
        units = [(3600, "h"), (60, "m"), (1, "s")]
        try:
            measure, unit = next((self.time / s, u) for s, u in units if self.time > s)
            return "{:.2f}{}".format(measure, unit)
        except StopIteration:
            return "{:.4f}s".format(self.time)
