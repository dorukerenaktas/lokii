from typing import TypedDict

import duckdb

TEMP_DB_PATH = ".temp/lokii.duckdb"


class NodeMetadata(TypedDict):
    run_key: str
    version: str
    gen_id: str


class NodeDataStorage:
    def __init__(self):
        """
        Temporary filesystem storage implementation for storing data generated between batches.
        It only stores data temporary and deletes all files after
        """
        self._conn = duckdb.connect(database=TEMP_DB_PATH, read_only=False)
        # create node meta table to store run generation information
        q = "CREATE TABLE IF NOT EXISTS main.__meta(run_key TEXT, version TEXT, gen_id TEXT, PRIMARY KEY(run_key));"
        self._conn.execute(q).fetchall()

    def meta(self, run_keys: list[str]) -> list[NodeMetadata]:
        """
        Fetches generation metadata information about given runs.
        :param run_keys: list of run ids
        :return: list of node meta dict
        """
        keys = ",".join([f"'{k}'" for k in run_keys])
        q = f"SELECT run_key, version, gen_id FROM main.__meta WHERE run_key IN ({keys});"
        data = self._conn.execute(q).df()
        return data.to_dict("records")

    def count(self, query: str) -> int:
        q = f"WITH _t AS ({query}) SELECT COUNT() FROM _t;"
        (count,) = self._conn.execute(q).fetchone()
        return count

    def exec(self, query: str, index: int, size: int) -> list[dict]:
        q = f"WITH _t AS ({query}) SELECT * FROM _t LIMIT {size} OFFSET {index * size};"
        data = self._conn.execute(q).df()
        return data.to_dict("records")

    def save(self, gen_id: str, run_key: str, version: str) -> None:
        """
        Generation id and node version will be stored in a meta table that can be used to check if gen run
        data is valid for consecutive runs.

        :param gen_id: identification of the generation process
        :param run_key: identification of the generation run
        :param version: node version of the module
        """
        q = f"""
        INSERT OR REPLACE INTO main.__meta(run_key, version, gen_id)
        VALUES ('{run_key}', '{version}', '{gen_id}');
        """
        self._conn.execute(q).fetchall()

    def insert(self, name: str, files: list[str]) -> None:
        """
        Creates a table for given node name in local relational database. If there is a table with the same
        node name it will drop all data and create a fresh one. Given files will be concatenated and inserted
        in the fresh table.

        :param name: node name of the module
        :param files: list of generated file paths
        """
        if "." in name:
            # create schema if node name defines `schema.table` syntax
            assert len(name.split(".")) == 2, "Nested schemas are not supported."
            schema = name.split(".")[0]
            q = f"CREATE SCHEMA IF NOT EXISTS {schema};"
            self._conn.execute(q).fetchall()

        # concatenate and insert file contents in a fresh table
        q = f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_json_auto({files});"
        self._conn.execute(q).fetchall()
