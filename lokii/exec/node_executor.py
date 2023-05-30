import math
from functools import partial
from typing import Callable

from pathos.pools import ProcessPool

from lokii.config import CONFIG
from lokii.model.node_module import GenNodeModule
from lokii.logger.progress import ProgressLogger
from lokii.storage.data_storage import DataStorage
from lokii.storage.temp_storage import TempStorage


def _exec_chunk(func: Callable, args: list[dict]):
    return [func(arg) for arg in args]


class NodeExecutor:
    def __init__(self, node: GenNodeModule, data_storage: DataStorage):
        """
        Reads and validates dataset configuration from filesystem structure.

        :param node: root path of the dataset generation
        :param data_storage: root path of the dataset generation
        """
        self.run = node
        self.data_storage = data_storage
        self.__temp_storage = TempStorage(self.run.name)

        # total times the gen function will be called
        self.t_count = 0
        # total generated item count
        self.g_count = 0

    def prepare_node(self) -> int:
        self.t_count = self.data_storage.count(self.run.source)
        return self.t_count

    def exec_node(self) -> list[str]:
        logger = ProgressLogger(self.t_count)
        batch_size = CONFIG.gen.batch_size
        batch_count = math.ceil(self.t_count / batch_size)

        for batch_index in range(batch_count):
            # calculate indexes from `f` to `t`
            f = batch_index * batch_size
            t = self.t_count if f + batch_size > self.t_count else f + batch_size

            params = self.data_storage.exec(self.run.source, batch_index, batch_size)
            args = [{"index": i, "id": i + 1, "params": params[i]} for i in range(f, t)]

            batch_result = []
            for chunk_result in self._exec_batch(args):
                batch_result.extend(chunk_result)
                logger.update(len(chunk_result))

            # save result to temp storage
            self.__temp_storage.dump(batch_result)
            self.g_count += len(batch_result)

        # return generated file paths
        return self.__temp_storage.batches

    def _exec_batch(self, args: list[dict]) -> list[dict]:
        chunk_size = CONFIG.gen.chunk_size
        chunk_args = [args[i : i + chunk_size] for i in range(0, len(args), chunk_size)]

        gen_func = partial(_exec_chunk, self.run.item)
        with ProcessPool(nodes=CONFIG.gen.concurrency) as pool:
            for chunk in pool.uimap(gen_func, chunk_args):
                # remove null items from generated chunk
                yield [i for i in chunk if i is not None]
