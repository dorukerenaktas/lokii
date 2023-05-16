from typing import TypedDict, List, Union, Literal, Optional, Any


class SimpleGenConfig(TypedDict):
    type: Literal["simple"]
    count: int
    rels: Optional[List[str]]


class MultiplyGenConfig(TypedDict):
    type: Literal["multiply"]
    mul: List[str]
    rels: Optional[List[str]]


class TableDefinition(TypedDict):
    cols: List[str]
    gen: Union[SimpleGenConfig, MultiplyGenConfig]


class DatasetTableDefinition(TypedDict):
    table_schema: str
    table_name: str
    table_def: TableDefinition
    table_gen: Any
