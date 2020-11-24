from typing import Any

from lokii.table.tools.tool import ITool, ToolContext


class ValueTool(ITool):
    def exec(self, ctx: ToolContext, args: Any = None) -> Any:
        assert args, "args must not be null for value tool." + self.to_string(ctx)
        if 'prop' in args:
            assert (args['prop'] in args), "Specified property not found in args." + self.to_string(ctx)
            return args[args['prop']]

        return args
