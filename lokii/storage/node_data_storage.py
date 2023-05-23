import duckdb

TEMP_DB_PATH = ".temp/lokii.duckdb"


class NodeDataStorage:
    def __init__(self):
        """
        Temporary filesystem storage implementation for storing data generated between batches.
        It only stores data temporary and deletes all files after
        """
        self._conn = duckdb.connect(database=TEMP_DB_PATH, read_only=False)

    def count(self, query: str) -> int:
        q = f"SELECT COUNT() FROM ({query});"
        (count,) = self._conn.execute(q).fetchone()
        return count

    def exec(self, query: str, index: int, size: int) -> list[dict]:
        q = f"SELECT * FROM ({query}) LIMIT {size} OFFSET {index * size};"
        data = self._conn.execute(q).df()
        return data.to_dict("records")
