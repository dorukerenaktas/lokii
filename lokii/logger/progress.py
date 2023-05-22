import logging
from io import StringIO

from tqdm import tqdm

from logger.color import style


class ProgressLogger(StringIO):
    def __init__(self, name: str, total: float):
        super(ProgressLogger, self).__init__()
        self.buf = None
        self.pbar = tqdm(
            total=total,
            desc=f"INFO  | {name} >",
            bar_format=style("{desc}", fg="cyan")
            + " {bar} "
            + style(
                "{percentage:3.0f}% {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
                fg="cyan",
            ),
            unit_scale=True,
            colour="CYAN",
        )

    def update(self, count: float):
        self.pbar.update(count)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pbar.close()
