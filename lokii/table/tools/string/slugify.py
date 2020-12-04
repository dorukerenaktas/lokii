from typing import Any
from slugify import slugify

from ..tool import ITool, ToolContext


class SlugifyTool(ITool):
    def exec(self, ctx: ToolContext, args: Any = None) -> Any:
        return slugify(args)
