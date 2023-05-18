from time import perf_counter


class PerformanceTimer:
    def __enter__(self):
        self.time = perf_counter()
        return self

    def __exit__(self, _, __, ___):
        self.time = perf_counter() - self.time
