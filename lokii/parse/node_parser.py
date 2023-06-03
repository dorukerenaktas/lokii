import logging
from os import path
from glob import glob

from lokii.config import CONFIG
from lokii.model.node_module import GenNodeModule
from lokii.util.module_file_loader import ModuleFileLoader
from lokii.util.perf_timer_context import PerfTimerContext
from lokii.parse.base_parser import BaseParser

logger = logging.getLogger("lokii.node_parser")
NODE_RESOLVER = "**/*%s" % CONFIG.gen.node_ext


class NodeParser(BaseParser):
    """
    Reads and validates node configurations from filesystem structure.

    :var nodes: parsed generation nodes
    :type nodes: dict[str, GenNodeModule]
    """

    def __init__(self, source_folder):
        """
        Initializes parser.
        :param source_folder: root path of the project
        :type source_folder: str
        """
        self.root = source_folder
        self.nodes = {}

    def parse(self):
        """
        :return: parsed and validated node run flat map
        :rtype: dict[str, GenNodeModule]
        """
        with PerfTimerContext() as t:
            nodes = list(self.__parse_nodes())
            self.nodes = {n.name: n for n in nodes}

        node_count = len(nodes)
        if node_count == 0:
            logger.warning("No generation node file found", extra={"at": self.root})
        else:
            logger.info("%d generation node parsed in %s" % (node_count, t))
        return self.nodes

    def __parse_nodes(self):
        """
        Finds all the nodes matching the node file pattern. Loads node modules and ensures
        node module configuration is valid.

        :return: parsed and validated node modules
        :rtype: list[GenNodeModule]
        """
        glob_path = path.join(self.root, NODE_RESOLVER)
        file_paths = [f for f in glob(glob_path, recursive=True)]

        for fp in file_paths:
            loader = ModuleFileLoader(fp)
            loader.load()
            mod = loader.module

            # extract node name from filename
            m_name = path.basename(fp).replace(CONFIG.gen.node_ext, "")
            # extract groups from file path
            m_groups = path.relpath(fp, self.root).split(path.sep)[:-1]
            m_version = loader.version

            # ensure provided module is valid
            self.attr(mod, "source", "`source` not found at %s" % fp)
            self.inst(mod.source, str, "`source` must be str at %s" % fp)
            self.attr(mod, "item", "`item` not found at %s" % fp)
            self.func(mod.item, "`item` must be function at %s" % fp)
            self.sig(mod.item, 1, "`item` accepts only one param at %s" % fp)
            if self.attr(mod, "name"):
                self.inst(mod.name, str, "`name` must be str at %s" % fp)
                m_name = mod.name

            parsed = GenNodeModule(mod.source, mod.item, m_name, m_version, m_groups)
            logger.debug("Found valid node `%s`", m_name, extra={"at": fp})
            yield parsed
