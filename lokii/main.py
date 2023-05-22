import logging
from os import makedirs, path

from lokii.logger import log_config
from lokii.model.gen_module import GenRun
from lokii.parse.gen_node_parser import GenNodeParser
from lokii.storage.storage_manager import StorageManager
from lokii.exec.gen_run_executor import GenRunExecutor
from lokii.util.perf_timer_context import PerfTimerContext


class Lokii:
    def __init__(self, source_folder: str, out_folder: str):
        """
        Generates massive amount of relational mock data.

        :param source_folder: path of root folder that contains schema and table definitions
        :param out_folder: path of output folder for mock data
        """
        self.__source_folder = source_folder
        self.__out_folder = out_folder

        self.__gen_parser = GenNodeParser(self.__source_folder)
        self.__storage = StorageManager()

    def generate(self):
        with PerfTimerContext() as t:
            # create out folder if not exists
            if not path.exists(self.__out_folder):
                makedirs(self.__out_folder)

            gen_runs = self.__gen_parser.parse()
            run_exec_order = self.__gen_parser.order()

            for run_key in run_exec_order:
                gen_run = gen_runs[run_key]
                self.generate_dataset(gen_run)
                self.__storage.save(gen_run.node_name)

        meta = self.__storage.all_meta()
        logging.info("Generation completed!")
        logging.info("Total target item count: {:,}".format(meta["target_count"]))
        logging.info("Generated {:,} items in {}\n".format(meta["item_count"], t))

    def generate_dataset(self, gen_run: GenRun):
        logger = logging.getLogger(gen_run.run_key)

        with PerfTimerContext() as t:
            executor = GenRunExecutor(gen_run, self.__storage)
            executor.prep()

            logger.info(
                "Generation started for target {:,} items".format(
                    executor.target_item_count
                )
            )
            executor.gen()

        meta = self.__storage.node_meta(gen_run.node_name)
        logger.info("{:,} items generated in {}\n".format(meta["item_count"], t))


if __name__ == "__main__":
    with log_config(verbose=logging.INFO):
        tabular = Lokii("../example/classicmodels", "./data")
        tabular.generate()
