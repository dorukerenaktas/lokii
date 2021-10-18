import math
import random
import time
from csv import DictWriter
from functools import partial
from os import makedirs, path, PathLike
from typing import Union, Dict

from pathos.multiprocessing import ProcessingPool

from .table import Table
from .utils import print_process


class Lokii:

    def __init__(self,
                 out_folder: Union[str, bytes, PathLike] = './data',
                 process_count: int = 8,
                 batch_size: int = 10000,
                 write_buffer_size: int = 50000,
                 index_cache_size: int = 50000,
                 random_cache_size: int = 20000,
                 silent: bool = False,
                 debug: bool = False):
        """
        Generates massive amount of relational mock data.

        :param out_folder: path of output folder for mock data
        """
        self.__out_folder = out_folder
        self._tables: Dict[str, Table] = {}

        self._process_count = process_count
        self._batch_size = batch_size
        self._index_cache_size = index_cache_size
        self._random_cache_size = random_cache_size
        self._silent = silent
        self._debug = debug

    def table(self, name: str) -> Table:
        table = Table(name, path.join(self.__out_folder, name + '.csv'), self._index_cache_size,
                      self._random_cache_size, self._debug)

        self._tables[name] = table
        return self._tables[name]

    def generate(self):
        # Create out folder if not exists
        if not path.exists(self.__out_folder):
            makedirs(self.__out_folder)

        for name, table in self._tables.items():
            print('GEN > {}'.format(name))
            t = time.time()

            table.prepare()
            self.__generate_table(name)

            elapsed_time = time.time() - t
            print('END > {}: {} rows in {:.4f}s\n'.format(name, table.gen_row_count, elapsed_time))

    def __generate_table(self, table_name: str):
        table = self._tables[table_name]

        with ProcessingPool(nodes=self._process_count) as pool:
            with open(table.outfile, 'w+', newline='', encoding='utf-8') as outfile:
                writer = DictWriter(outfile, fieldnames=[name for name in table.columns])
                writer.writeheader()

                # Write defaults
                writer.writerows(table.defaults)
                table.row_count += len(table.defaults)
                table.gen_row_count += len(table.defaults)

                while table.row_count < table.target_count:
                    batch_start = table.row_count
                    batch_end = batch_start + self._batch_size \
                        if batch_start + self._batch_size < table.target_count \
                        else table.target_count

                    if table.is_product:
                        # If it is a product table load index cache of multiplicand
                        table.multiplicand.load_index_cache(
                            math.floor(batch_start / len(table.multiplier)),
                            math.floor(batch_end / len(table.multiplier)))

                    for rel in table.relations:
                        # Load random cache for all relation tables
                        rel.load_random_cache(batch_start / table.target_count)

                    if table.multiplicand:
                        rel_dicts = \
                            [
                                {
                                    table.multiplicand.name: table.multiplicand.get_row(
                                        math.floor(index / len(table.multiplier))),
                                    **{r.name: r.get_rand(index - batch_start)
                                       for i, r in enumerate(table.relations)}
                                }
                                for index in range(batch_start, batch_end)
                            ]
                    else:
                        rel_dicts = \
                            [
                                {
                                    r.name: r.get_rand(index - batch_start)
                                    for i, r in enumerate(table.relations)
                                }
                                for index in range(batch_start, batch_end)
                            ]

                    result = pool.map(
                        table.gen_func,
                        [index + 1 for index in range(batch_start, batch_end)], rel_dicts)

                    # Remove none rows
                    result = list(filter(None, result))

                    writer.writerows(result)
                    table.row_count = batch_end
                    table.gen_row_count += len(result)
                    print_process(table.row_count, table.target_count)
        print('')
        # Generation completed purge caches
        if table.is_product:
            # If it is a product table purge multiplicand cache
            table.multiplicand.purge_cache()

        for rel in table.relations:
            # Purge cache for all relation tables
            rel.purge_cache()
