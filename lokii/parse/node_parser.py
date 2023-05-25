from __future__ import annotations

import logging
import glob
import inspect
from os import path

from lokii.config import CONFIG
from lokii.model.gen_module import GenNodeModule, GenRunConf, GenRun
from lokii.util.module_file_loader import ModuleFileLoader
from lokii.util.perf_timer_context import PerfTimerContext


class NodeParser:
    def __init__(self, source_folder: str):
        """
        Reads and validates dataset configuration from filesystem structure.

        :param source_folder: root path of the dataset generation schema
        """
        self.root = source_folder
        self.gen_runs: dict[str, GenRun] = {}

    def parse(self) -> dict[str, GenRun]:
        with PerfTimerContext() as t:
            gen_nodes = list(self.__parse_nodes())
            self.gen_runs = {
                GenRun.create_key(n.name, i): GenRun(n.name, n.version, i, r)
                for n in gen_nodes
                for i, r in enumerate(n.runs)
            }

        node_count = len(gen_nodes)
        run_count = len(self.gen_runs)
        if node_count == 0:
            logging.warning(f"No generation node file found at {self.root}")
        else:
            logging.info("Total {} runs found.".format(run_count))
            logging.info("{} generation node parsed in {}".format(node_count, t))
        return self.gen_runs

    def __parse_nodes(self) -> list[GenNodeModule] | None:
        glob_path = path.join(self.root, f"**/*{CONFIG.gen.file_ext}")
        file_paths = [f for f in glob.glob(glob_path)]

        for fp in file_paths:
            loader = ModuleFileLoader(fp)
            loader.load()
            m = loader.module

            assert hasattr(m, "runs"), f"`runs` configuration not found at {fp}"
            assert m.runs is not None, f"`runs` configuration not found at {fp}"
            assert isinstance(m.runs, list), f"`runs` must be list at {fp}"
            assert len(m.runs) > 0, f"`runs` has no items at {fp}"

            parsed = GenNodeModule()
            parsed.name = path.basename(fp).replace(CONFIG.gen.file_ext, "")
            parsed.version = loader.version
            if hasattr(m, "name"):
                parsed.name = m.name
            if hasattr(m, "version"):
                parsed.version = m.version

            runs: list[GenRunConf] = []
            for i, r in enumerate(m.runs):
                runs.append(self.__parse_run(i, r, fp))

            parsed.runs = runs
            yield parsed

    def __parse_run(self, i: int, r: GenRunConf, fp: str) -> GenRunConf:
        assert "source" in r, f"runs[{i}][`source`] not found at {fp}"
        if not isinstance(r["source"], str):
            raise AssertionError(f"runs[{i}][`source`] must be str at {fp}")
        if "wait" not in r:
            r["wait"] = []
        elif not isinstance(r["wait"], list):
            raise AssertionError(f"runs[{i}][`wait`] must be list at {fp}")
        if "func" not in r:
            raise AssertionError(f"runs[{i}][`func`] not found at {fp}")
        elif not inspect.isfunction(r["func"]):
            raise AssertionError(f"runs[{i}][`func`] must be function at {fp}")
        elif len(inspect.signature(r["func"]).parameters) != 1:
            raise AssertionError(
                f"runs[{i}][`func`] must accept only one parameter at {fp}"
            )
        return r
