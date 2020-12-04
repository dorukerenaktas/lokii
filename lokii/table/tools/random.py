import random
from typing import Any

from .tool import ITool, ToolContext


class RandomTool(ITool):
    def exec(self, ctx: ToolContext, args: Any = None) -> Any:
        assert hasattr(random, args['func']), "Specified function must be in random" + self.to_string(ctx)
        func = getattr(random, args['func'])
        params = args['params'] if 'params' in args else {}
        return func(**params)
