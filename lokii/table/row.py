from typing import Dict, Collection

from faker import Faker

from ..config import ColumnOption
from .column import Column
from .tools.tool import ToolContext


class Row:
    def __init__(self, table: str, cols: Dict[str, Collection[ColumnOption]]):
        self.table = table
        self.cols = [Column(name, cols[name]) for name in cols]

    def exec(self, index: int, lang: str, fake: Faker, rel: Dict[str, Dict] = None):
        if rel is None:
            rel = {}

        ctx: ToolContext = {
            'table': self.table,
            'col': '',
            'index': index,
            'lang': lang,
            'fake': fake,
            'curr': {},
            'rel': rel
        }

        row = {}
        for col in self.cols:
            ctx['col'] = col.name
            row[col.name] = col.exec(ctx)
            ctx['curr'] = dict(ctx['curr'], **row)
        return row
