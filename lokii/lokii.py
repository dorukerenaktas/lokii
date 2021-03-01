from os import makedirs, path, PathLike
from typing import Union, List

from .table import Table


class Lokii:

    def __init__(self, out: Union[str, bytes, PathLike] = './data', process_count: int = 8, batch_size: int = 10000,
                 write_buffer_size: int = 50000, index_cache_size: int = 50000, random_cache_size: int = 2000,
                 debug: bool = False):
        """
        Generates massive amount of relational mock data.

        :param out: path of output folder for mock data
        """
        self._out = out
        self._tables: List[Table] = []

        self._process_count = process_count
        self._batch_size = batch_size
        self._index_cache_size = index_cache_size
        self._random_cache_size = random_cache_size
        self._debug = debug

        # Create out folder if not exists
        if not path.exists(out):
            makedirs(out)

    def table(self, name: str):
        table = Table(name, path.join(self._out, name + '.csv'), self._process_count, self._batch_size,
                      self._index_cache_size, self._random_cache_size, self._debug)
        self._tables.append(table)
        return table
