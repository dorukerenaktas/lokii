import logging
import os
import shutil
import uuid

from lokii.config import CONFIG
from lokii.storage.data_storage import DataStorage
from lokii.model.node_module import GenNodeModule
from lokii.parse.node_parser import NodeParser
from lokii.parse.group_parser import GroupParser
from lokii.util.perf_timer_context import PerfTimerContext
from lokii.util.graph_analyzer import GraphAnalyzer
from lokii.exec.node_executor import NodeExecutor


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
        self.__node_parser = NodeParser(self.__source_folder)
        self.__group_parser = GroupParser(self.__source_folder)

    def generate(self, purge: bool = False):
        with PerfTimerContext() as t:
            nodes = self.__node_parser.parse()
            # create dependency map from node source queries
            dep_map = [
                (n.name, [d for d in self.__data_storage.deps(n.source) if d in nodes])
                for n in nodes.values()
            ]
            analyzer = GraphAnalyzer(dep_map)
            exec_order = analyzer.execution_order()

            total_target_count, total_item_count = 0, 0
            for name in exec_order:
                run = nodes[name]
                dep_keys = analyzer.dependencies(name)
                if self.is_node_valid(run, dep_keys):
                    logging.info("%s not changed. Using existing dataset." % name)
                    continue

                # generate dataset
                target_count, item_count, file_paths = self.generate_node(run)
                total_target_count += target_count
                total_item_count += item_count

                # save generation metadata in database
                self.__data_storage.save(self.__gen_id, run.name, run.version)
                # insert generated data in database
                self.__data_storage.insert(run.name, file_paths)

        logging.info("Generation completed!")
        logging.info("Total target item count: {:,}".format(total_target_count))
        logging.info("Generated {:,} items in {}".format(total_item_count, t))
        self.__data_storage.export(self.__out_folder, "csv")
        Lokii.clean_env(purge)

    def generate_node(self, node: GenNodeModule) -> (int, int, list[str]):
        with PerfTimerContext() as t:
            logger = logging.getLogger(node.name)

            executor = NodeExecutor(node, self.__data_storage)
            target_count = executor.prepare_node()

            logger.info("Generation started for target {:,} items".format(target_count))
            generated_file_paths = executor.exec_node()
            item_count = executor.g_count

        logger.info("{:,} items generated in {}".format(item_count, t))
        return target_count, item_count, generated_file_paths

    def is_node_valid(self, node: GenNodeModule, dep_keys: list[str]):
        metadata = self.__data_storage.meta(dep_keys)
        curr = [m for m in metadata if m["name"] == node.name]
        if len(curr) == 0:
            # no dataset generated before with this run key
            return False  # must generate
        if curr[0]["version"] != node.version:
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
