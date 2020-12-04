from typing import Any

from .tool import ITool, ToolContext


class ContextTool(ITool):
    def exec(self, ctx: ToolContext, args: Any = None) -> Any:
        assert ('key' in args), "No key specified for context" + self.to_string(ctx)
        if isinstance(args['key'], list):
            curr = ctx
            for key in args['key']:
                assert (key in curr), "Specified key not found for context" + self.to_string(ctx)
                curr = curr[key]
            return curr

        assert (args['key'] in ctx), "Specified key not found for context" + self.to_string(ctx)
        return ctx[args['key']]
