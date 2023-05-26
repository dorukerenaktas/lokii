from io import StringIO
from tqdm import tqdm


class ProgressLogger(StringIO):
    def __init__(self, total: float):
        super(ProgressLogger, self).__init__()
        self.total = total
        fmt = " ".join(
            [
                "{bar}",
                "{percentage:3.0f}%",
                "{n_fmt}/{total_fmt}",
                "[{elapsed}<{remaining}, {rate_fmt}{postfix}]",
            ]
        )
        self.pbar = tqdm(total=total, bar_format=fmt, unit_scale=True, leave=False)

    def update(self, count: float):
        self.pbar.update(count)
        if count / self.total == 1:
            self.pbar.close()
