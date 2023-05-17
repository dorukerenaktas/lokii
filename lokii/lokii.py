import time
from os import makedirs, path, PathLike
from typing import Union

from model.fake_data_config import FakeDataConfig
from model.execution_config import ExecutionConfig
from tabular.dataset_config_reader import DatasetConfigReader
from tabular.dataset_generator import DatasetGenerator
from tabular.dataset_storage_service import DatasetStorageService


class Lokii:

    def __init__(self,
                 root_folder: Union[str, bytes, PathLike] = './schemas',
                 out_folder: Union[str, bytes, PathLike] = './data',
                 fake_config: FakeDataConfig = None,
                 exec_config: ExecutionConfig = None,
                 process_count: int = 8,
                 batch_size: int = 100000):
        """
        Generates massive amount of relational mock data.

        :param root_folder: path of root folder that contains schema and table definitions
        :param out_folder: path of output folder for mock data
        """
        self.__root_folder = root_folder
        self.__out_folder = out_folder

        if fake_config is None:
            self.__fake_conf = {"langs": ["tr", "en"], "seed": None}

        if exec_config is None:
            self.__exec_conf = {"process_count": 6, "batch_size": 1000, "cache_size": 100000}

        self.__conf_reader = DatasetConfigReader(self.__root_folder)
        self.__storage = DatasetStorageService()
        self._process_count = process_count
        self._batch_size = batch_size

    def generate(self):
        # create out folder if not exists
        if not path.exists(self.__out_folder):
            makedirs(self.__out_folder)

        self.__conf_reader.prepare()
        execution_order = self.__conf_reader.execution_order()

        for table_name in execution_order:
            print('GEN > {}'.format(table_name))
            t = time.perf_counter()

            table = self.__conf_reader.tables[table_name]
            generator = DatasetGenerator(table, self.__fake_conf, self.__exec_conf, self.__storage)
            generator.generate()

            elapsed_time = time.perf_counter() - t
            print('END > {}: {} rows in {:.4f}s\n'.format(table_name, 'table.gen_row_count',
                                                          elapsed_time))
    #
    # def __generate_table(self, table_config: Dict):
    #     with ProcessingPool(nodes=self._process_count) as pool:
    #         with open(table.outfile, 'w+', newline='', encoding='utf-8') as outfile:
    #             writer = DictWriter(outfile, fieldnames=[name for name in table.columns])
    #             writer.writeheader()
    #
    #             # Write defaults
    #             writer.writerows(table.defaults)
    #             table.processed_row_count += len(table.defaults)
    #             table.gen_row_count += len(table.defaults)
    #
    #             while table.processed_row_count < table.target_count:
    #                 batch_start = table.processed_row_count
    #                 batch_end = batch_start + self._batch_size \
    #                     if batch_start + self._batch_size < table.target_count \
    #                     else table.target_count
    #
    #                 if table.is_product:
    #                     # If it is a product table load index cache of multiplicand
    #                     table.multiplicand.load_index_cache(
    #                         math.floor(batch_start / len(table.multiplier)),
    #                         math.floor(batch_end / len(table.multiplier)))
    #
    #                 for rel in table.relations:
    #                     # Load random cache for all relation tables
    #                     rel.load_random_cache(batch_start / table.target_count)
    #
    #                 if table.multiplicand:
    #                     rel_dicts = \
    #                         [
    #                             {
    #                                 table.multiplicand.name: table.multiplicand.get_row(
    #                                     math.floor(index / len(table.multiplier))),
    #                                 **{r.name: r.get_rand(index - batch_start)
    #                                    for i, r in enumerate(table.relations)}
    #                             }
    #                             for index in range(batch_start, batch_end)
    #                         ]
    #                 else:
    #                     rel_dicts = \
    #                         [
    #                             {
    #                                 r.name: r.get_rand(index - batch_start)
    #                                 for i, r in enumerate(table.relations)
    #                             }
    #                             for index in range(batch_start, batch_end)
    #                         ]
    #
    #                 result = pool.map(
    #                     table.gen_func,
    #                     [index + 1 for index in range(batch_start, batch_end)], rel_dicts)
    #
    #                 # Remove none rows
    #                 result = list(filter(None, result))
    #
    #                 writer.writerows(result)
    #                 table.processed_row_count = batch_end
    #                 table.gen_row_count += len(result)
    #                 print_process(table.processed_row_count, table.target_count)
    #     print('')
    #     # Generation completed purge caches
    #     if table.is_product:
    #         # If it is a product table purge multiplicand cache
    #         table.multiplicand.purge_cache()
    #
    #     for rel in table.relations:
    #         # Purge cache for all relation tables
    #         rel.purge_cache()


if __name__ == "__main__":
    tabular = Lokii(root_folder=path.abspath("../example/classicmodels"))
    tabular.generate()
