from typing import Any

from ..tool import ITool, ToolContext


class JoinTool(ITool):
    def exec(self, ctx: ToolContext, args: Any = None) -> Any:
        assert ('sep' in args), "No separator specified for join function" + self.to_string(ctx)
        assert ('parts' in args), "No parts specified for join function" + self.to_string(ctx)
        return str(args['sep']).join(args['parts'])
