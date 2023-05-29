import logging
import glob
import inspect
from os import path

from lokii.config import CONFIG
from lokii.model.node_module import GenNodeModule, GenRun
from lokii.util.module_file_loader import ModuleFileLoader
from lokii.util.perf_timer_context import PerfTimerContext

NODE_RESOLVER = "**/*%s" % CONFIG.gen.node_ext


class NodeParser:
    """
    Reads and validates node configurations from filesystem structure.

    :var nodes: parsed generation nodes
    :type nodes: dict[str, GenNodeModule]
    :var runs: parsed generation runs
    :type runs: dict[str, GenRun]
    """

    def __init__(self, source_folder):
        """
        Initializes parser.
        :param source_folder: root path of the project
        :type source_folder: str
        """
        self.root = source_folder
        self.nodes = {}
        self.runs = {}

    def parse(self):
        """
        :return: parsed and validated node run flat map
        :rtype: dict[str, GenRun]
        """
        with PerfTimerContext() as t:
            nodes = list(self.__parse_nodes())
            self.nodes = {n.name: n for n in nodes}
            self.runs = {
                GenRun.create_key(n.name, i): GenRun(n.name, n.version, i, r)
                for n in nodes
                for i, r in enumerate(n.runs)
            }

        node_count = len(nodes)
        run_count = len(self.runs)
        if node_count == 0:
            logging.warning("No generation node file found at %s" % self.root)
        else:
            logging.info("Total %d runs found." % run_count)
            logging.info("%d generation node parsed in %s" % (node_count, t))
        return self.runs

    def __parse_nodes(self):
        """
        Finds all the nodes matching the node file pattern. Loads node modules and ensures
        node module configuration is valid.

        :return: parsed and validated node modules
        :rtype: list[GenNodeModule]
        """
        glob_path = path.join(self.root, NODE_RESOLVER)
        file_paths = [f for f in glob.glob(glob_path)]

        for fp in file_paths:
            loader = ModuleFileLoader(fp)
            loader.load()
            module = loader.module

            # check required conditions
            assert hasattr(module, "runs"), "`runs` configuration not found at %s" % fp
            assert module.runs is not None, "`runs` configuration not found at %s" % fp
            assert isinstance(module.runs, list), "`runs` must be list at %s" % fp
            assert len(module.runs) > 0, "`runs` has no items at %s" % fp

            m_name = path.basename(fp).replace(CONFIG.gen.node_ext, "")
            m_version = loader.version
            m_groups = path.relpath(fp, self.root).split(path.sep)[:-1]
            parsed = GenNodeModule(loader.module.runs, m_name, m_version, m_groups)

            # check optional conditions
            if hasattr(module, "name") and module.name is not None:
                parsed.name = module.name
            if hasattr(module, "version") and module.version is not None:
                parsed.version = module.version

            runs = []
            for i, r in enumerate(module.runs):
                # ensure run configuration is valid
                AE = AssertionError
                assert "source" in r, "runs[%d][`source`] not found at %s" % (i, fp)
                if not isinstance(r["source"], str):
                    raise AE("runs[%d][`source`] must be str at %s" % (i, fp))
                if "wait" not in r:
                    r["wait"] = []
                elif not isinstance(r["wait"], list):
                    raise AE("runs[%d][`wait`] must be list at %s" % (i, fp))
                if "func" not in r or r["func"] is None:
                    raise AE("runs[%d][`func`] not found at %s" % (i, fp))
                elif not inspect.isfunction(r["func"]):
                    raise AE("runs[%d][`func`] must be function at %s" % (i, fp))
                elif len(inspect.signature(r["func"]).parameters) != 1:
                    raise AE("runs[%d][`func`] accepts only one param at %s" % (i, fp))
                runs.append(r)

            parsed.runs = runs
            yield parsed
