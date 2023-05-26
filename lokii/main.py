import logging
import os
import shutil
import uuid

from lokii.config import CONFIG
from lokii.model.gen_module import GenRun
from lokii.parse.node_parser import NodeParser
from lokii.parse.graph_analyzer import GraphAnalyzer
from lokii.storage.data_storage import DataStorage
from lokii.exec.gen_executor import GenExecutor
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
        self.__gen_id = str(uuid.uuid4())

        Lokii.setup_env()
        self.__data_storage = DataStorage()
        self.__gen_parser = NodeParser(self.__source_folder)

    def generate(self, purge: bool = False):
        with PerfTimerContext() as t:
            gen_runs = self.__gen_parser.parse()
            analyzer = GraphAnalyzer(list(gen_runs.values()))
            run_exec_order = analyzer.execution_order()

            total_target_count, total_item_count = 0, 0
            for run_key in run_exec_order:
                run = gen_runs[run_key]
                dep_keys = analyzer.dependencies(run_key)
                if self.is_dataset_valid(run, dep_keys):
                    logging.info(f"{run_key} not changed. Using existing dataset.")
                    continue

                # generate dataset
                target_count, item_count, file_paths = self.generate_dataset(run)
                total_target_count += target_count
                total_item_count += item_count

                # save generation metadata in database
                self.__data_storage.save(self.__gen_id, run.run_key, run.node_version)
                # insert generated data in database
                self.__data_storage.insert(run.node_name, file_paths)

        logging.info("Generation completed!")
        logging.info("Total target item count: {:,}".format(total_target_count))
        logging.info("Generated {:,} items in {}".format(total_item_count, t))
        self.__data_storage.export(self.__out_folder, "csv")
        Lokii.clean_env(purge)

    def generate_dataset(self, gen_run: GenRun) -> (int, int, list[str]):
        with PerfTimerContext() as t:
            logger = logging.getLogger(gen_run.run_key)

            executor = GenExecutor(gen_run, self.__data_storage)
            target_count = executor.prepare_node()

            logger.info("Generation started for target {:,} items".format(target_count))
            generated_file_paths = executor.exec_node()
            item_count = executor.g_count

        logger.info("{:,} items generated in {}".format(item_count, t))
        return target_count, item_count, generated_file_paths

    def is_dataset_valid(self, run: GenRun, dep_keys: list[str]):
        metadata = self.__data_storage.meta([*dep_keys, run.run_key])
        curr = [m for m in metadata if m["run_key"] == run.run_key]
        if len(curr) == 0:
            # no dataset generated before with this run key
            return False  # must generate
        if curr[0]["version"] != run.node_version:
            # code version is different from previous run
            return False  # must regenerate
        for dep_meta in metadata:
            if dep_meta["gen_id"] == self.__gen_id:
                # dependent dataset changed in current generation
                return False  # must regenerate
        # no code changes, no dependencies changed
        return True  # dataset is valid, do not regenerate

    @staticmethod
    def setup_env():
        Lokii.clean_env(False)
        if not os.path.exists(CONFIG.temp.data_path):
            os.makedirs(CONFIG.temp.data_path)

    @staticmethod
    def clean_env(force: bool = False):
        if force and os.path.exists(CONFIG.temp.dir_path):
            shutil.rmtree(CONFIG.temp.dir_path)
        elif os.path.exists(CONFIG.temp.data_path):
            shutil.rmtree(CONFIG.temp.data_path)
