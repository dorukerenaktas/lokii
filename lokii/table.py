import random
from typing import Dict, Callable, List, Any, Optional

import pandas as pd


class Table:
    def __init__(self,
                 name: str,
                 outfile: str,
                 index_cache_size: int,
                 random_cache_size: int,
                 debug: bool):
        """
        Database table like data structure definition that hold column and general configuration to
        adjust generated data.

        :param name: name of the table
        """
        self.name = name
        self.outfile = outfile
        self.columns = None
        self.relations: List["Table"] = []
        self.defaults: List[Dict] = []

        # Determine if table is product of a multiplication
        self.is_product = False
        # Multiplicand table, for each row in this table multiplier length of rows will be generated
        self.multiplicand: Optional["Table"] = None
        # Multiplier of the pivot table
        self.multiplier: List[Any] = [1]

        self.gen_func = lambda x: x

        # The number of rows to be created
        self.target_count = 0
        # Processed number of target rows
        self.row_count = 0
        # Number of generated rows
        self.gen_row_count = 0

        self._index_cache_size = index_cache_size
        self._random_cache_size = random_cache_size
        self._debug = debug

        self._row_cache = []
        self._row_cache_start = -1
        self._row_cache_end = -1

    def cols(self, *cols: str) -> "Table":
        """
        Adds columns to table. Generated output will be ordered by given columns order.

        :param cols: name of the columns
        """
        if len(cols) <= 1:
            # In order to use row cache (Pandas to dict oriented as records) there must be two or more rows
            raise KeyError('Table {} must have 2 or more columns'.format(self.name))

        dup = {x for x in cols if cols.count(x) > 1}
        if len(dup) > 0:
            raise KeyError('Columns {} are duplicated for table {}'.format(dup, self.name))
        self.columns = cols
        return self

    def rels(self, *tables: "Table") -> "Table":
        """
        Adds relations to the table. For every generated row, a random row will be selected from
        relation tables.

        :param tables: the relation tables
        """
        dup = {x for x in tables if tables.count(x) > 1}
        if len(dup) > 0:
            raise KeyError('Relations {} are duplicated for table {}'.format(dup, self.name))

        self.relations = tables
        return self

    def defs(self, defaults: List[Dict]) -> "Table":
        """
        Adds default rows to the table. Every default row must have all required columns.

        :param defaults: default rows for the table
        """
        for i, d in enumerate(defaults):
            if not all(k in self.columns for k in d):
                raise KeyError('Default row at index {} does have all required columns for table {}'
                               .format(i, self.name))

        self.defaults = defaults
        return self

    def simple(self, count: int, gen: Callable[[int, Dict], Dict]) -> "Table":
        self.target_count = count

        def generate_row(index: int, rel_dict: Dict) -> Dict:
            return gen(index, rel_dict)

        # self._write_async(100 if self._debug else count, generate_row)
        self.gen_func = generate_row
        return self

    def multiply(self, table: "Table", gen: Callable[[int, Any, Dict], Dict],
                 multiplier: List) -> "Table":
        if len(multiplier) == 0:
            raise KeyError('Table {} has a multiplier with no items'.format(self.name))

        self.is_product = True
        self.multiplicand = table
        self.multiplier = multiplier if multiplier else [1]

        def generate_row(index: int, rel_dict: Dict) -> Dict:
            return gen(index, multiplier[index % len(multiplier)], rel_dict)

        # self._write_async(count, generate_row)
        self.gen_func = generate_row
        return self

    def prepare(self):
        if self.is_product:
            self.target_count = self.multiplicand.gen_row_count * len(self.multiplier)

    def load_index_cache(self, start: int, end: int) -> None:
        """
        Index cache is used for multiplying. Before starting batch jobs pivot table needs to cache all
        range of required indexes.
        :param start index of range
        :param end index of range
        """
        if self._row_cache_start <= start and end <= self._row_cache_end:
            # Already have all required indexes, do nothing
            return

        if start + self._index_cache_size > self.gen_row_count:
            # Remaining range is smaller than cache size, cache all remaining
            self._row_cache_start = start
            self._row_cache_end = self.gen_row_count
        else:
            # Cache range from start to start + cache size
            self._row_cache_start = start
            self._row_cache_end = start + self._index_cache_size

        dfs = pd.read_csv(self.outfile, sep=',', header=0, names=self.columns,
                          skiprows=self._row_cache_start,
                          chunksize=self._row_cache_end - self._row_cache_start, squeeze=True)
        df = pd.concat(dfs)
        self._row_cache = df.to_dict(orient='records')

    def load_random_cache(self, process: float):
        """
        Random cache is used for relations. Before starting batch jobs relation table needs to cache
        range of random indexes.

        :param process completion ratio of the process
        """
        curr = int(self.gen_row_count * process)
        if self._row_cache_start <= curr <= self._row_cache_end:
            # Already have all required indexes, do nothing
            return

        if curr + self._random_cache_size > self.gen_row_count:
            # Remaining range is smaller than cache size, cache all remaining
            self._row_cache_start = curr
            self._row_cache_end = self.gen_row_count
        else:
            # Cache range from start to start + cache size
            self._row_cache_start = curr
            self._row_cache_end = curr + self._random_cache_size

        dfs = pd.read_csv(self.outfile, sep=',', header=0, names=self.columns,
                          skiprows=self._row_cache_start,
                          chunksize=self._row_cache_end - self._row_cache_start, squeeze=True)
        df = pd.concat(dfs)
        self._row_cache = df.to_dict(orient='records')
        random.shuffle(self._row_cache)

    def purge_cache(self):
        """
        Purge cache after generation process end.
        """
        self._row_cache = []
        self._row_cache_start = -1
        self._row_cache_end = -1

    def get_row(self, index: int):
        if index >= self.gen_row_count:
            raise IndexError('Index {} is not valid for table {}'.format(index, self.name))

        if self._row_cache_start > index or self._row_cache_end < index:
            raise IndexError('Index {} is not cached for table {}, cache range {}-{} of {}'
                             .format(index, self.name, self._row_cache_start, self._row_cache_end,
                                     self.gen_row_count))

        return self._row_cache[index - self._row_cache_start]

    def get_rand(self, seed: int):
        index = seed % self.gen_row_count \
            if self._random_cache_size > self.gen_row_count \
            else seed % self._random_cache_size
        return self._row_cache[index]
