from typing import Collection

from lokii.types import ColumnOption
from lokii.table.tools import tools
from lokii.table.tools.tool import ToolContext


class Column:
    def __init__(self, name: str, data: Collection[ColumnOption]):
        self.name = name
        self.options = data

    def exec(self, ctx: ToolContext):
        result = None
        for option in self.options:
            args = option['args'] if 'args' in option else None
            args = result if result is not None else args
            result = tools[option['type']](ctx, args)

        return result
