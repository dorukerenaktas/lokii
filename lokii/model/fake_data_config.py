from typing import TypedDict, List, Optional


class FakeDataConfig(TypedDict):
    langs: List[str]
    seed: Optional[int]
