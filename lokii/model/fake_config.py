from typing import TypedDict, List, Optional


class FakeConfig(TypedDict):
    langs: List[str]
    seed: Optional[int]
