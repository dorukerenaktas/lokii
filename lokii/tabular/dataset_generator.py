from __future__ import annotations

import time
import math
from functools import partial

from faker import Faker
from pathos.pools import ProcessPool
from typing import Callable, Any

from model.execution_config import ExecutionConfig
from model.fake_data_config import FakeDataConfig

from model.table_definition import DatasetTableDefinition
from tabular.dataset_storage_service import DatasetStorageService


def gen_func(func: Callable, from_index: int, to_index: int, args: Any):
    result = []
    for i in range(from_index, to_index - 1):
        result.append(func(i, args[i - from_index]))
    return result


class DatasetGenerator:
    def __init__(
        self,
        table_conf: DatasetTableDefinition,
        fake_conf: FakeDataConfig,
        exec_conf: ExecutionConfig,
        storage: DatasetStorageService,
    ):
        """
        Generates dataset according to given configuration.

        :param table_conf: source path of the tabular schema structure
        :param fake_conf: source path of the tabular schema structure
        """
        self.__table_config = table_conf
        self.__gen_config = self.__table_config["table_def"]["gen"]
        self.__exec_conf = exec_conf
        self.__fake_conf = fake_conf["langs"]
        self.__storage = storage

    def generate(self):
        if self.__gen_config["type"] == "simple":
            self.__generate_simple()
        elif self.__gen_config["type"] == "product":
            self.__generate_product()

    def __generate_simple(self):
        t = time.perf_counter()
        target_row_count = self.__gen_config["count"]
        batch_size = self.__exec_conf["batch_size"]
        batch_count = math.ceil(target_row_count / batch_size)
        generated_row_count = 0

        fake_conf = {
            "d": Faker(),
            "a": Faker(self.__fake_conf),
            "l": {lng: Faker([lng]) for lng in self.__fake_conf},
        }

        conf = {"f": fake_conf}

        run_config = []
        for batch_index in range(batch_count):
            from_index = batch_index * batch_size
            to_index = (
                from_index + batch_size
                if from_index + batch_size < target_row_count
                else target_row_count
            )

            for rel in self.__gen_config["rels"]:
                # Load random cache for all relation tables
                self.__storage.query(rel)

            args = [conf for i in range(from_index, to_index)]
            run_config.append((from_index, to_index, args))

        elapsed_time = time.perf_counter() - t
        print('PRE > {} row data prep in {:.4f}s\n'.format(target_row_count, elapsed_time))

        table_gen_func = partial(gen_func, self.__table_config["table_gen"])
        with ProcessPool(nodes=self.__exec_conf["process_count"]) as pool:
            result = pool.map(table_gen_func, *map(list, zip(*run_config)))
            generated_row_count += len(result)
        print(generated_row_count)
        return []

    def __generate_product(self):
        return []
