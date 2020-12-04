from typing import Collection

from ..config import ColumnOption
from .tools import tools
from .tools.tool import ToolContext


class Column:
    def __init__(self, name: str, data: Collection[ColumnOption]):
        self.name = name
        self.options = data

    def exec(self, ctx: ToolContext):
        calc = []
        for option in self.options:
            args = option['args'] if 'args' in option else {}

            assert ('type' in option), "Type not specified for column option! " + self.name
            assert (option['type'] in tools), "Tool can not be found! " + option['type']

            if 'calc' in option:
                if isinstance(option['calc']['keys'], list):
                    calc_values = []
                    for index in option['calc']['keys']:
                        calc_values.append(calc[index])
                else:
                    calc_values = calc[option['calc']['keys']]

                if 'as' in option['calc']:
                    args[option['calc']['as']] = calc_values
                else:
                    args = calc_values
            calc.append(tools[option['type']].exec(ctx, args))

        return calc[-1:][0] if len(calc) > 0 else None
