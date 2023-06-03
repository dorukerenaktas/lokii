import logging
import os.path
from functools import partial

import duckdb
from typing import TypedDict, Callable

from lokii.config import CONFIG

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
                "CREATE TABLE IF NOT EXISTS __meta"
                "(name TEXT, version TEXT, gen_id TEXT, PRIMARY KEY(name));"
            )
            conn.execute(q).fetchall()

    def deps(self, query: str) -> list:
        names = duckdb.get_table_names(query)
        return list(names)

    def count(self, query: str) -> int:
        q = "WITH _t AS (%s) SELECT COUNT() FROM _t;" % query
        try:
            with self.connect() as conn:
                (count,) = conn.execute(q).fetchone()
                return count
        except duckdb.Error as err:
            logging.error("Error occurred while executing count query:\n\n%s\n" % q)
            raise err

    def exec(self, query: str, index: int, size: int) -> list[dict]:
        args = (query, size, index * size)
        q = "WITH _t AS (%s) SELECT * FROM _t LIMIT %d OFFSET %d;" % args
        try:
            with self.connect() as conn:
                data = conn.execute(q).fetch_df()
                return data.to_dict("records")
        except duckdb.Error as err:
            logging.error("Error occurred while executing source query:\n\n%s\n" % q)
            raise err

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
            INSERT OR REPLACE INTO __meta(name, version, gen_id)
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
            q = "SELECT name, version, gen_id FROM __meta WHERE name IN (%s);"
            data = conn.execute(q % keys).fetch_df()
            return data.to_dict("records")

    def cols(self, name) -> list[str]:
        """
        Fetches generated column name list for given node.
        :param name: name of the node
        :type name: str
        :return: list of no columns
        """
        with self.connect() as conn:
            q = "DESCRIBE %s;"
            data = conn.execute(q % name).fetchall()
            return [col[0] for col in data]

    def insert(self, name: str, files: list[str]) -> None:
        """
        Creates a table for given node name in local relational database. If there is a table
        with the same node name it will drop all data and create a fresh one. Given files will
        be concatenated and inserted in the fresh table.

        :param name: node name of the module
        :param files: list of generated file paths
        """
        with self.connect() as conn:
            assert "." not in name, "Node names can not contain dot(.) = %s" % name

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
