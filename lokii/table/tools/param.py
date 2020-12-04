from typing import Any

from .tool import ITool, ToolContext


class ParamTool(ITool):
    def exec(self, ctx: ToolContext, args: Any = None) -> Any:
        assert ('key' in args), "No key specified for args" + self.to_string(ctx)
        if isinstance(args['key'], list):
            curr = args
            for key in args['key']:
                assert (key in curr), "Specified key not found for args" + self.to_string(ctx)
                curr = curr[key]
            return curr

        assert (args['key'] in args), "Specified key not found for args" + self.to_string(ctx)
        return args[args['key']]
