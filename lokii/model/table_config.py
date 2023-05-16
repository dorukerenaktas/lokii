from typing import TypedDict, List, Union, Literal, Optional


class SimpleGenConfig(TypedDict):
    type: Literal["simple"]
    count: int
    rels: Optional[List[str]]


class MultiplyGenConfig(TypedDict):
    type: Literal["multiply"]
    mul: List[str]
    rels: Optional[List[str]]


class TableConfig(TypedDict):
    cols: List[str]
    gen: Union[SimpleGenConfig, MultiplyGenConfig]
