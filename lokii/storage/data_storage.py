import os.path
from functools import partial

import duckdb
from typing import TypedDict

from lokii.config import CONFIG

CONN: duckdb.DuckDBPyConnection


class NodeMetadata(TypedDict):
    run_key: str
    version: str
    gen_id: str


class DataStorage:
    def __init__(self):
        """
        Temporary filesystem storage implementation for storing data generated between batches.
        It only stores data temporary and deletes all files after
        """
        self.connect = partial(duckdb.connect, database=CONFIG.temp.db_path)
        with self.connect() as conn:
            # create node meta table to store run generation information
            q = (
                "CREATE TABLE IF NOT EXISTS main.__meta"
                "(run_key TEXT, version TEXT, gen_id TEXT, PRIMARY KEY(run_key));"
            )
            conn.execute(q).fetchall()

    def count(self, query: str) -> int:
        with self.connect() as conn:
            q = f"WITH _t AS ({query}) SELECT COUNT() FROM _t;"
            (count,) = conn.execute(q).fetchone()
            return count

    def exec(self, query: str, index: int, size: int) -> list[dict]:
        with self.connect() as conn:
            q = f"WITH _t AS ({query}) SELECT * FROM _t LIMIT {size} OFFSET {index * size};"
            data = conn.execute(q).df()
            return data.to_dict("records")

    def save(self, gen_id: str, run_key: str, version: str) -> None:
        """
        Generation id and node version will be stored in a meta table that can be used to check
        if gen run data is valid for consecutive runs.

        :param gen_id: identification of the generation process
        :param run_key: identification of the generation run
        :param version: node version of the module
        """
        with self.connect() as conn:
            q = f"""
            INSERT OR REPLACE INTO main.__meta(run_key, version, gen_id)
            VALUES ('{run_key}', '{version}', '{gen_id}');
            """
            conn.execute(q).fetchall()

    def meta(self, run_keys: list[str]) -> list[NodeMetadata]:
        """
        Fetches generation metadata information about given runs.
        :param run_keys: list of run ids
        :return: list of node meta dict
        """
        with self.connect() as conn:
            keys = ",".join([f"'{k}'" for k in run_keys])
            q = f"SELECT run_key, version, gen_id FROM main.__meta WHERE run_key IN ({keys});"
            data = conn.execute(q).df()
            return data.to_dict("records")

    def insert(self, name: str, files: list[str]) -> None:
        """
        Creates a table for given node name in local relational database. If there is a table
        with the same node name it will drop all data and create a fresh one. Given files will
        be concatenated and inserted in the fresh table.

        :param name: node name of the module
        :param files: list of generated file paths
        """
        with self.connect() as conn:
            if "." in name:
                # create schema if node name defines `schema.table` syntax
                assert len(name.split(".")) == 2, "Nested schemas are not supported."
                schema = name.split(".")[0]
                q = f"CREATE SCHEMA IF NOT EXISTS {schema};"
                conn.execute(q).fetchall()

            # concatenate and insert file contents in a fresh table
            q = f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_json_auto({files});"
            conn.execute(q).fetchall()

    def export(self, out_path: str, fmt: str) -> None:
        """
        Exports all generated tables to given file format.

        :param out_path: folder path of the exported files
        :param fmt: file format of the exported files
        """
        with self.connect() as conn:
            tables = conn.execute("SHOW TABLES;").fetchall()
            # exclude meta table from export list
            tables = [f for (f,) in tables if "__meta" != f]

            # create out folder if not exists
            if not os.path.exists(out_path):
                os.makedirs(out_path)

            for t in tables:
                path = os.path.join(out_path, f"{t}.{fmt}")
                # export to output path
                conn.execute(f"COPY {t} TO '{path}'").fetchone()
