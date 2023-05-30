import os.path
from functools import partial

import duckdb
from typing import TypedDict

from lokii.config import CONFIG

CONN = None  #: duckdb.DuckDBPyConnection

NodeMetadata = TypedDict("NodeMetadata", {"name": str, "version": str, "gen_id": str})


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
                "(name TEXT, version TEXT, gen_id TEXT, PRIMARY KEY(name));"
            )
            conn.execute(q).fetchall()

    def count(self, query: str) -> int:
        with self.connect() as conn:
            q = "WITH _t AS (%s) SELECT COUNT() FROM _t;" % query
            (count,) = conn.execute(q).fetchone()
            return count

    def exec(self, query: str, index: int, size: int) -> list[dict]:
        with self.connect() as conn:
            q = "WITH _t AS (%s) SELECT * FROM _t LIMIT %d OFFSET %d;"
            data = conn.execute(q % (query, size, index * size)).df()
            return data.to_dict("records")

    def save(self, gen_id: str, name: str, version: str) -> None:
        """
        Generation id and node version will be stored in a meta table that can be used to check
        if gen run data is valid for consecutive runs.

        :param gen_id: identification of the generation process
        :param name: identification of the node
        :param version: the code version of the module
        """
        with self.connect() as conn:
            q = """
            INSERT OR REPLACE INTO main.__meta(name, version, gen_id)
            VALUES ('%s', '%s', '%s');
            """
            conn.execute(q % (name, version, gen_id)).fetchall()

    def meta(self, names: list[str]) -> list[NodeMetadata]:
        """
        Fetches generation metadata information about given runs.
        :param names: list of node names
        :return: list of node meta dict
        """
        with self.connect() as conn:
            keys = ",".join(["'%s'" % n for n in names])
            q = "SELECT name, version, gen_id FROM main.__meta WHERE name IN (%s);"
            data = conn.execute(q % keys).df()
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
                q = "CREATE SCHEMA IF NOT EXISTS %s;"
                conn.execute(q % schema).fetchall()

            # concatenate and insert file contents in a fresh table
            q = "CREATE OR REPLACE TABLE %s AS SELECT * FROM read_json_auto(%s);"
            conn.execute(q % (name, files)).fetchall()

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
                path = os.path.join(out_path, ".".join([t, fmt]))
                # export to output path
                conn.execute("COPY %s TO '%s'" % (t, path)).fetchone()
