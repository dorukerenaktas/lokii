from typing import Any

from .tool import ITool, ToolContext


class FakerTool(ITool):
    def exec(self, ctx: ToolContext, args: Any = None) -> Any:
        assert hasattr(ctx['fake'], args['func']), "Specified function must be in faker" + self.to_string(ctx)
        fake = ctx['fake']
        if 'unique' in args:
            fake = fake.unique
        func = getattr(fake, args['func'])
        params = args['params'] if 'params' in args else {}
        return func(**params)
