import math
import time

import pandas as pd
from pathos.multiprocessing import ProcessingPool
import random
from csv import DictWriter
from typing import Dict, Callable, List, Any


class Table:
    def __init__(self, name: str, outfile: str, process_count: int, batch_size: int, index_cache_size: int,
                 random_cache_size: int, debug: bool):
        """
        Database table like data structure definition that hold column and general configuration to
        adjust generated data.

        :param name: name of the table
        """
        self.name = name
        self._outfile = outfile
        self._cols = None
        self._relations: List["Table"] = []
        self._defaults: List[Dict] = []

        self._pivot: "Table" = None
        self._pivot_mul_count: int = 1

        self._index = 0
        self._count = 0

        self.row_count = 0

        self._process_count = process_count
        self._batch_size = batch_size
        self._index_cache_size = index_cache_size
        self._random_cache_size = random_cache_size
        self._debug = debug

        self._row_cache = []
        self._row_cache_start = -1
        self._row_cache_end = -1

    def cols(self, *cols: List[str]) -> "Table":
        """
        Adds columns to table. Generated output will be ordered by given columns order.

        :param cols: name of the columns
        """
        dup = {x for x in cols if cols.count(x) > 1}
        if len(dup) > 0:
            raise KeyError('Columns {} are duplicated for table {}'.format(dup, self.name))
        self._cols = cols
        return self

    def rel(self, *tables: List["Table"]) -> "Table":
        """
        Adds relation to the table. For every generated row, a random row will be selected from relation tables.

        :param tables: the relation table
        """
        dup = {x for x in tables if tables.count(x) > 1}
        if len(dup) > 0:
            raise KeyError('Relations {} are duplicated for table {}'.format(dup, self.name))

        self._relations = tables
        return self

    def defaults(self, defaults: List[Dict]) -> "Table":
        """
        Adds default rows to the table. Every default row must have all required columns.

        :param defaults: default rows for the table
        """
        for i, d in enumerate(defaults):
            if all(k in self._cols for k in d):
                raise KeyError(
                    'Default row at index {} does have all required columns for table {}'.format(i, self.name))

        self._defaults = defaults
        return self

    def simple(self, count: int, gen: Callable[[int, Dict], Dict]) -> "Table":
        def generate_row(index: int, rel_dict: Dict) -> Dict:
            return gen(index, rel_dict)

        self._write_async(100 if self._debug else count, generate_row)
        return self

    def multiply(self, table: "Table", gen: Callable[[int, Any, Dict], Dict], multiplier: List = None) -> "Table":
        self._pivot = table
        self._pivot_mul_count = 1 if multiplier is None else len(multiplier)

        mul_count = self._pivot_mul_count
        count = table.row_count * mul_count

        def generate_row(index: int, rel_dict: Dict) -> Dict:
            return gen(index, multiplier[index % len(multiplier)], rel_dict)

        self._write_async(count, generate_row)
        return self

    def load_index_cache(self, start: int, end: int) -> None:
        """
        Index cache is used for multiplying. Before starting batch jobs pivot table needs to cache all
        range of required indexes.
        :param start where batch job start at
        :param end where batch job end at
        """
        if self._row_cache_start <= start and end <= self._row_cache_end:
            # Already have all required indexes, do nothing
            return

        if start + self._index_cache_size > self.row_count:
            # Remaining range is smaller than cache size, cache all remaining
            self._row_cache_start = start
            self._row_cache_end = self.row_count
        else:
            # Cache range from start to start + cache size
            self._row_cache_start = start
            self._row_cache_end = start + self._index_cache_size

        dfs = pd.read_csv(self._outfile, sep=',', header=0, names=self._cols, skiprows=self._row_cache_start,
                          chunksize=self._row_cache_end - self._row_cache_start, squeeze=True)
        df = pd.concat(dfs)
        self._row_cache = df.to_dict(orient='records')
        print('Indexes cached for table {} from {} to {} total {}'
              .format(self.name, self._row_cache_start, self._row_cache_end, len(self._row_cache)))

    def load_random_cache(self):
        """
        Random cache is used for relations. Before starting batch jobs relation table needs to cache
        range of random indexes.
        """
        self._row_cache_start = random.randrange(self.row_count - self._random_cache_size)
        self._row_cache_end = self._row_cache_start + self._random_cache_size

        dfs = pd.read_csv(self._outfile, sep=',', header=0, names=self._cols, skiprows=self._row_cache_start,
                          chunksize=self._row_cache_end - self._row_cache_start, squeeze=True)
        df = pd.concat(dfs)
        self._row_cache = df.to_dict(orient='records')

    def purge_cache(self):
        """
        Purge cache after generation process end.
        """
        self._row_cache = []
        self._row_cache_start = -1
        self._row_cache_end = -1

    def get_index_row(self, index: int):
        if index >= self.row_count:
            raise IndexError('Index {} is not valid for table {}'.format(index, self.name))

        if self._row_cache_start > index or self._row_cache_end < index:
            raise IndexError('Index {} is not cached for table {}, cache range {}-{} of {}'
                             .format(index, self.name, self._row_cache_start, self._row_cache_end, self.row_count))

        return self._row_cache[index - self._row_cache_start]

    def get_random_row(self):
        index = random.randint(self._row_cache_start, self._row_cache_end)
        return self.get_index_row(index)

    def _write_async(self, count: int, worker: Callable[[int, Dict], Dict]):
        t = time.time()
        with ProcessingPool(nodes=self._process_count) as pool:
            with open(self._outfile, 'w+', newline='', encoding='utf-8') as outfile:
                writer = DictWriter(outfile, fieldnames=[name for name in self._cols])
                writer.writeheader()

                print('Generation started for table {}'.format(self.name))
                # Write defaults
                writer.writerows(self._defaults)
                self.row_count += len(self._defaults)

                while self.row_count < count:
                    batch_start = self.row_count
                    batch_end = batch_start + self._batch_size if batch_start + self._batch_size < count else count

                    if self._pivot:
                        # If pivot table available load index cache
                        self._pivot.load_index_cache(math.floor(batch_start / self._pivot_mul_count),
                                                     math.floor(batch_end / self._pivot_mul_count))

                    for rel in self._relations:
                        # Load random cache for all relation tables
                        rel.load_random_cache()

                    if self._pivot:
                        rel_dicts = [
                            {
                                **{rel.name: rel.get_random_row() for rel in self._relations},
                                self._pivot.name: self._pivot.get_index_row(math.floor(index / self._pivot_mul_count))
                            }
                            for index in range(batch_start, batch_end)]
                    else:
                        rel_dicts = [
                            {rel.name: rel.get_random_row() for rel in self._relations}
                            for _ in range(batch_start, batch_end)
                        ]

                    result = pool.map(worker, [index for index in range(batch_start, batch_end)], rel_dicts)

                    writer.writerows(result)
                    self.row_count = batch_end
                    print('#', end='', flush=True)

        print('')
        # Generation completed purge caches
        if self._pivot:
            # If pivot table available purge cache
            self._pivot.purge_cache()

        for rel in self._relations:
            # Purge cache for all relation tables
            rel.purge_cache()

        elapsed_time = time.time() - t
        print('Generated {} rows for table {} in {:.4f}s'.format(self.row_count, self.name, elapsed_time))
