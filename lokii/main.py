import logging
import os
import shutil
import uuid

from lokii.config import CONFIG
from lokii.storage.data_storage import DataStorage
from lokii.storage.batch_iterator import BatchIterator
from lokii.model.node_module import GenNodeModule
from lokii.parse.node_parser import NodeParser
from lokii.parse.group_parser import GroupParser
from lokii.util.perf_timer_context import PerfTimerContext
from lokii.util.graph_analyzer import GraphAnalyzer
from lokii.exec.node_executor import NodeExecutor

logger = logging.getLogger("lokii")


class Lokii:
    def __init__(self, source_folder: str):
        """
        Generates massive amount of relational mock data.

        :param source_folder: path of root folder that contains schema and table definitions
        """
        self.__source_folder = source_folder
        self.__gen_id = str(uuid.uuid4())

        Lokii.setup_env()
        self.__data_storage = DataStorage()
        self.__node_parser = NodeParser(self.__source_folder)
        self.__group_parser = GroupParser(self.__source_folder)

    def generate(self, export: bool = False, purge: bool = False):
        with PerfTimerContext() as t:
            nodes = self.__node_parser.parse()

            # create dependency map from node source queries
            dep_map = list(self.order_nodes(nodes))
            analyzer = GraphAnalyzer(dep_map)
            exec_order = analyzer.execution_order()

            total_target_count, total_item_count = 0, 0
            for name in exec_order:
                run = nodes[name]
                dep_keys = analyzer.dependencies(name)
                if self.is_node_valid(run, dep_keys):
                    logger.info("%s not changed. Using existing dataset." % name)
                    continue

                # generate dataset
                target_count, item_count, file_paths = self.generate_node(run)
                total_target_count += target_count
                total_item_count += item_count

                # save generation metadata in database
                self.__data_storage.save(self.__gen_id, run.name, run.version)
                # insert generated data in database
                self.__data_storage.insert(run.name, file_paths)

        logger.info("Generation completed!")
        logger.info("Total target item count: {:,}".format(total_target_count))
        logger.info("Generated {:,} items in {}".format(total_item_count, t))

        if export:
            self.export(nodes)
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

    def export(self, nodes):
        exported = {n: False for n in nodes.keys()}
        with PerfTimerContext() as t:
            groups = self.__group_parser.parse()
            group_nodes = {
                g: [n.name for n in nodes.values() if g in n.groups]
                for g in groups.keys()
            }
            # create dependency map from node source queries
            dep_map = [
                (g.name, [gr for gr in g.groups if gr in groups])
                for g in groups.values()
            ]
            analyzer = GraphAnalyzer(dep_map)
            exec_order = analyzer.execution_order()

            # start from root and exec found `before` functions
            for name in exec_order:
                logger = logging.getLogger(name)
                if groups[name].before:
                    logger.info("Executing before()")
                    groups[name].before({"nodes": group_nodes[name]})
                else:
                    logger.info("before() not executed.")

            # start from leafs and exec found `export` functions
            for name in exec_order[::-1]:
                logger = logging.getLogger(name)
                if groups[name].export:
                    exports = [
                        k
                        for k in nodes.keys()
                        if not exported[k] and k in group_nodes[name]
                    ]
                    for n in exports:
                        logger.info("Executing export() for node %s" % n)
                        cols = self.__data_storage.cols(n)
                        # execute export function for each node in this group
                        iterator = BatchIterator(self.__data_storage, n)
                        groups[name].export(
                            {"name": n, "cols": cols, "batches": iterator}
                        )
                        exported[n] = True
                else:
                    logger.info("export() not executed.")

            # start from leafs and exec found `after` functions
            for name in exec_order[::-1]:
                logger = logging.getLogger(name)
                if groups[name].after:
                    logger.info("Executing after()")
                    groups[name].after({"nodes": group_nodes[name]})
                else:
                    logger.info("after() not executed.")
        export_count = len([k for k in exported.keys() if exported[k]])
        logger.info("{:,} nodes exported in {}".format(export_count, t))

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

    def order_nodes(self, nodes):
        for n in nodes.values():
            # get dependencies in node source query
            deps = self.__data_storage.deps(n.source)
            # check if dependency exists in parsed nodes
            for dep in deps:
                if dep not in nodes:
                    raise AssertionError(
                        "Dependency `%s` in node source query is not found!\n"
                        "Node: %s" % (dep, n.name)
                    )
            logger.debug("Dependencies found for `%s`: %s" % (n.name, deps))
            yield n.name, deps

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
