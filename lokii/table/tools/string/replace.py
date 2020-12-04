from typing import Any

from ..tool import ITool, ToolContext


class ReplaceTool(ITool):
    def exec(self, ctx: ToolContext, args: Any = None) -> Any:
        assert ('string' in args), "No string specified for replace function" + self.to_string(ctx)
        assert ('old' in args), "No old specified for replace function" + self.to_string(ctx)
        assert ('new' in args), "No new specified for replace function" + self.to_string(ctx)
        return str(args['string']).replace(args['old'], args['new'])
