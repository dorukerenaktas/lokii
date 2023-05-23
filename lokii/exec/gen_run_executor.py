from __future__ import annotations

import math
from functools import partial
from typing import Callable
from pathos.pools import ProcessPool

from lokii.logger.progress import ProgressLogger
from lokii.model.gen_module import GenRun
from lokii.storage.storage_manager import StorageManager
from storage.node_batch_storage import NodeBatchStorage

CONCURRENCY = 8
BATCH_SIZE = 100000
CHUNK_SIZE = 200


def _exec_chunk(func: Callable, args: list[dict]):
    return [func(arg) for arg in args]


class GenRunExecutor:
    def __init__(self, run: GenRun, storage: StorageManager):
        """
        Reads and validates dataset configuration from filesystem structure.

        :param run: root path of the dataset generation
        """
        self.run = run
        self.__batch_storage: NodeBatchStorage | None = None
        self.storage = storage

        # total times the gen function will be called
        self.target_item_count = 0

    def prepare_node(self) -> int:
        target_count = self.storage.count(self.run.source)

        self.__batch_storage = NodeBatchStorage(self.run.node_name, target_count)
        self.target_item_count = target_count
        self.storage.node_init(self.run.node_name, self.target_item_count)
        return self.target_item_count

    def exec_node(self):
        logger = ProgressLogger(self.run.run_key, self.target_item_count)
        batch_count = math.ceil(self.target_item_count / BATCH_SIZE)
        for batch_index in range(batch_count):
            from_index = batch_index * BATCH_SIZE
            to_index = from_index + BATCH_SIZE
            if to_index > self.target_item_count:
                to_index = self.target_item_count

            params = self.storage.exec(self.run.source, batch_index, BATCH_SIZE)
            args = [
                {"index": i, "id": i + 1, "params": params[i]}
                for i in range(from_index, to_index)
            ]

            chunk_args = [
                args[i : i + CHUNK_SIZE] for i in range(0, len(args), CHUNK_SIZE)
            ]

            result = []
            gen_func = partial(_exec_chunk, self.run.func)
            with ProcessPool(nodes=CONCURRENCY) as pool:
                for chunk in pool.uimap(gen_func, chunk_args):
                    cleaned = [i for i in chunk if i is not None]
                    result.extend(cleaned)
                    logger.update(len(chunk))

            self.storage.dump(self.run.node_name, batch_index, result)
