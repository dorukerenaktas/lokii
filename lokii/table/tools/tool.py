import json
from typing import Any, TypedDict, Dict

from faker import Faker


class ToolContext(TypedDict):
    table: str
    col: str
    index: int
    lang: str
    fake: Faker
    curr: Dict
    rel: Dict[str, Dict]


class ITool:
    def exec(self, ctx: ToolContext, args: Any = None) -> Any:
        """Overrides InformalParserInterface.load_data_source()"""
        pass

    @staticmethod
    def to_string(ctx: ToolContext):
        return json.dumps(ctx)
