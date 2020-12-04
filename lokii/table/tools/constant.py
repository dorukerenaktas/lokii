from typing import Any

from .tool import ITool, ToolContext


class ConstantTool(ITool):
    def exec(self, ctx: ToolContext, args: Any = None) -> Any:
        return args
