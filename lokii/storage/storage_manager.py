import json
import duckdb
from functools import reduce
from os import path, makedirs
from typing import TypedDict, Dict, List

TEMP_STORAGE_DIR = ".temp/data"
TEMP_DB_STORAGE_DIR = ".temp/lokii.duckdb"


class StorageMeta(TypedDict):
    target_count: int
    item_count: int
    batch_count: int


class GenNodeStorageMeta(StorageMeta):
    node_name: str


class GenNodeBatchPartition(TypedDict):
    file_path: str
    item_count: int


def batch_storage_key(name: str, batch_index: int):
    return "__".join([name, str(batch_index)])


class StorageManager:
    def __init__(self):
        """
        Reads and validates dataset configuration from filesystem structure.
        """
        self.__meta: Dict[str, GenNodeStorageMeta] = {}
        self.__storage_map: Dict[str, Dict[int, GenNodeBatchPartition]] = {}

        if not path.exists(TEMP_STORAGE_DIR):
            makedirs(TEMP_STORAGE_DIR)
        self._conn = duckdb.connect(database=TEMP_DB_STORAGE_DIR, read_only=False)

    def node_init(self, name: str, target: int) -> None:
        self.__storage_map[name] = {}
        self.__meta[name] = {
            "node_name": name,
            "target_count": target,
            "item_count": 0,
            "batch_count": 0,
        }

    def node_meta(self, name: str) -> GenNodeStorageMeta:
        if name not in self.__meta:
            raise KeyError(f"Provided key {name} not found in temp storage.")
        return self.__meta[name]

    def all_meta(self) -> StorageMeta:
        meta: StorageMeta = {"target_count": 0, "item_count": 0, "batch_count": 0}
        for name in self.__meta:
            node_meta = self.__meta[name]
            meta["target_count"] += node_meta["target_count"]
            meta["item_count"] += node_meta["item_count"]
            meta["batch_count"] += node_meta["batch_count"]
        return meta

    def load(self, name: str, batch_index: int) -> List[Dict]:
        storage_path = self.__storage_map[name][batch_index]["file_path"]

        with open(storage_path, "r") as _f:
            return json.load(_f)

    def dump(self, name: str, batch_index: int, batch_data: List[Dict]) -> None:
        storage_key = batch_storage_key(name, batch_index)
        storage_path = path.join(TEMP_STORAGE_DIR, storage_key + ".json")

        with open(storage_path, "w") as _f:
            _f.write(json.dumps(batch_data))

        self.__storage_map[name][batch_index] = {
            "file_path": storage_path,
            "item_count": len(batch_data),
        }

        parts = self.__storage_map[name].values()
        self.__meta[name]["batch_count"] = len(parts)
        self.__meta[name]["item_count"] = reduce(
            lambda a, c: a + c["item_count"], parts, 0
        )

    def exec(self, query: str, index: int, size: int) -> list[dict]:
        q = f"SELECT * FROM ({query}) LIMIT {size} OFFSET {index * size};"
        data = self._conn.execute(q).df()
        return data.to_dict("records")

    def count(self, query: str) -> int:
        q = f"SELECT COUNT() FROM ({query});"
        (count,) = self._conn.execute(q).fetchone()
        return count

    def save(self, name: str) -> None:
        if "." in name:
            assert len(name.split(".")) == 2, "Nested schemas are not supported."
            schema = name.split(".")[0]
            q = f"CREATE SCHEMA IF NOT EXISTS {schema};"
            self._conn.execute(q).fetchall()

        file_paths = [f["file_path"] for f in self.__storage_map[name].values()]
        q = f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_json_auto({file_paths});"
        self._conn.execute(q).fetchall()
