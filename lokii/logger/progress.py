from io import StringIO
from tqdm import tqdm

from .color import style


class ProgressLogger(StringIO):
    def __init__(self, total: float):
        super(ProgressLogger, self).__init__()
        self.total = total
        self.pbar = tqdm(
            total=total,
            bar_format="{bar} "
            + style(
                "{percentage:3.0f}% {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
                fg="cyan",
            ),
            unit_scale=True,
            colour="CYAN",
        )

    def update(self, count: float):
        self.pbar.update(count)
        if count / self.total == 1:
            self.pbar.close()
