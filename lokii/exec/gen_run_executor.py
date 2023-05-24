from __future__ import annotations

import math
from functools import partial
from typing import Callable
from pathos.pools import ProcessPool

from lokii.logger.progress import ProgressLogger
from lokii.model.gen_module import GenRun
from storage.node_data_storage import NodeDataStorage
from storage.temp_batch_storage import TempBatchStorage

CONCURRENCY = 8
BATCH_SIZE = 100000
CHUNK_SIZE = 200


def _exec_chunk(func: Callable, args: list[dict]):
    return [func(arg) for arg in args]


class GenRunExecutor:
    def __init__(self, run: GenRun, data_storage: NodeDataStorage):
        """
        Reads and validates dataset configuration from filesystem structure.

        :param run: root path of the dataset generation
        :param data_storage: root path of the dataset generation
        """
        self.run = run
        self.data_storage = data_storage
        self.__temp_storage = TempBatchStorage(self.run.node_name)
        self.__logger: ProgressLogger

        # total times the gen function will be called
        self.target_item_count = 0
        # total generated item count
        self.gen_item_count = 0

    def prepare_node(self) -> int:
        target_count = self.data_storage.count(self.run.source)
        self.target_item_count = target_count
        return self.target_item_count

    def exec_node(self) -> list[str]:
        logger = ProgressLogger(self.run.run_key, self.target_item_count)
        batch_count = math.ceil(self.target_item_count / BATCH_SIZE)
        for batch_index in range(batch_count):
            from_index = batch_index * BATCH_SIZE
            to_index = from_index + BATCH_SIZE
            if to_index > self.target_item_count:
                to_index = self.target_item_count

            params = self.data_storage.exec(self.run.source, batch_index, BATCH_SIZE)
            args = [
                {"index": i, "id": i + 1, "params": params[i]}
                for i in range(from_index, to_index)
            ]

            batch_result = []
            for chunk_result in self._exec_batch(args):
                batch_result.extend(chunk_result)
                logger.update(len(chunk_result))

            # save result to temp storage
            self.__temp_storage.dump(batch_result)
            self.gen_item_count += len(batch_result)

        # return generated file paths
        return self.__temp_storage.batches

    def _exec_batch(self, args: list[dict]) -> list[dict]:
        chunk_args = [args[i : i + CHUNK_SIZE] for i in range(0, len(args), CHUNK_SIZE)]

        gen_func = partial(_exec_chunk, self.run.func)
        with ProcessPool(nodes=CONCURRENCY) as pool:
            for chunk in pool.uimap(gen_func, chunk_args):
                # remove null items from generated chunk
                yield [i for i in chunk if i is not None]
