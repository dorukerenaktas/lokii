from __future__ import annotations

import logging
import glob
import inspect
import networkx as nx
from os import path

from typing import cast, List, Dict

from util.module_file_loader import ModuleFileLoader
from model.gen_module import GenNodeModule, GenRunConf, GenRun
from util.perf_timer_context import PerfTimerContext

GEN_CONF_FILE_EXT = ".gen.py"


class GenNodeParser:
    def __init__(self, root_path: str):
        """
        Reads and validates dataset configuration from filesystem structure.

        :param root_path: root path of the dataset generation schema
        """
        self.root = root_path
        self.gen_nodes: Dict[str, GenNodeModule] = {}
        self.gen_runs: Dict[str, GenRun] = {}

    def parse(self) -> Dict[str, GenRun]:
        with PerfTimerContext() as t:
            self.gen_nodes = {n.name: n for n in self.__parse_gen_nodes()}
            self.gen_runs = {
                GenRun.create_key(n.name, i): GenRun(n.name, i, r)
                for n in self.gen_nodes.values()
                for i, r in enumerate(n.runs)
            }

        node_count = len(self.gen_nodes)
        run_count = len(self.gen_runs)
        if node_count == 0:
            logging.warning(f"No generation node file found at {self.root}")
        else:
            logging.info("Total {} runs found.".format(run_count))
            logging.info("{} generation node parsed in {}".format(node_count, t))
        return self.gen_runs

    def order(self):
        dig = nx.DiGraph()
        for run in self.gen_runs.values():
            if not run.wait:
                dig.add_node(run.run_key)
            for dep in run.wait:
                dig.add_edge(dep, run.run_key)

        cycles = list(nx.simple_cycles(dig))
        if len(cycles) != 0:
            raise AssertionError(f"Found cyclic dependencies!\n{cycles}")
        return list(nx.topological_sort(dig))

    def __parse_gen_nodes(self) -> List[GenNodeModule] | None:
        glob_path = path.join(self.root, f"**/*{GEN_CONF_FILE_EXT}")
        file_paths = [f for f in glob.glob(glob_path)]

        for fp in file_paths:
            ml = ModuleFileLoader(fp)
            m = cast(GenNodeModule, ml.load())

            assert hasattr(m, "runs"), f"`runs` configuration not found at {fp}"
            assert m.runs is not None, f"`runs` configuration not found at {fp}"
            assert isinstance(m.runs, list), f"`runs` must be list at {fp}"
            assert len(m.runs) > 0, f"`runs` has no items at {fp}"

            parsed = GenNodeModule()
            parsed.name = path.basename(fp).replace(GEN_CONF_FILE_EXT, "")
            if hasattr(m, "name"):
                parsed.name = m.name

            runs: List[GenRunConf] = []
            for i, r in enumerate(m.runs):
                if "source" not in r:
                    r["source"] = f"SELECT * FROM {parsed.name}"
                elif not isinstance(r["source"], str):
                    raise AssertionError(f"runs[{i}][`source`] must be str at {fp}")
                if "wait" not in r:
                    r["wait"] = []
                elif not isinstance(r["wait"], list):
                    raise AssertionError(f"runs[{i}][`wait`] must be list at {fp}")
                if "rels" not in r:
                    r["rels"] = {}
                elif not isinstance(r["rels"], dict):
                    raise AssertionError(f"runs[{i}][`rels`] must be dict at {fp}")
                if "func" not in r:
                    raise AssertionError(f"runs[{i}][`func`] not found at {fp}")
                elif not inspect.isfunction(r["func"]):
                    raise AssertionError(f"runs[{i}][`func`] must be function at {fp}")
                elif len(inspect.signature(r["func"]).parameters) != 1:
                    raise AssertionError(
                        f"runs[{i}][`func`] must accept only one parameter at {fp}"
                    )
                runs.append(r)

            parsed.runs = runs
            yield parsed
