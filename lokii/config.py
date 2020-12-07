from typing import Collection, Dict, TypedDict, Any


class ColumnOption(TypedDict):
    type: str
    args: Any


class TableOption(TypedDict):
    type: str
    index_start: int
    args: Dict


class TableConfig(TypedDict):
    name: str
    option: TableOption
    cols: Dict[str, Collection[ColumnOption]]
    default: Collection[Dict]


class LokiConfig(TypedDict):
    languages: Collection[str]
    tables: Collection[TableConfig]
