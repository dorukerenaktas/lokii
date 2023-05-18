from __future__ import annotations

import logging
import sys
import glob
import inspect
import json
import networkx as nx
from os import path, sep

from typing import List, Any, cast

from importlib.util import spec_from_file_location, module_from_spec

from data.loader import DatasetModuleLoader
from model.proj_conf import ProjectConfigModule
from model.gen_conf import GenerationConfigModule, TableDefinition
from tabular.dataset_constants import TABLE_DEF_FILE_EXTENSION, TABLE_GEN_FILE_EXTENSION
from util.perf import PerformanceTimer

PROJ_CONF_FILE_EXT = "conf.py"
GEN_CONF_FILE_EXT = "gen.py"


class DatasetConfigParser:
    def __init__(self, root_path: str):
        """
        Reads and validates dataset configuration from filesystem structure.

        :param root_path: root path of the dataset generation schema
        """
        self.root = root_path
        self.proj_conf: ProjectConfigModule | None = None
        self.gen_confs: List[GenerationConfigModule] = []

    def prepare(self):
        with PerformanceTimer() as t:
            self.proj_conf = self.__parse_proj_conf()
        if not self.proj_conf:
            logging.info("Project conf file not found. Using defaults.")
        else:
            logging.info("Project configuration parsed in {:.4f}s".format(t.time))

        with PerformanceTimer() as t:
            self.gen_confs = list(self.__parse_gen_confs())
        conf_count = len(self.gen_confs)
        if conf_count == 0:
            logging.warning(f"No generation files found at {self.root}")
        else:
            logging.info("{} gen files parsed in {:.4f}s".format(conf_count, t.time))

        # read all table definitions from given path
        glob_path = path.join(self.root, f"**/*{TABLE_DEF_FILE_EXTENSION}")
        file_paths = [f for f in glob.glob(glob_path)]

        tables = {}
        for p in file_paths:
            [table_schema, table_name] = DatasetConfigParser.get_table_namespace(
                self.root, p
            )
            table_def = DatasetConfigParser.get_table_def(p)
            table_gen = DatasetConfigParser.get_table_gen(table_name, p)

            table_namespace = f"{table_schema}.{table_name}"
            tables[table_namespace] = {
                "table_schema": table_schema,
                "table_name": table_name,
                "table_def": table_def,
                "table_gen": table_gen,
            }
        self.tables = tables

    def __parse_proj_conf(self) -> ProjectConfigModule | None:
        glob_path = path.join(self.root, f"**.{PROJ_CONF_FILE_EXT}")
        file_paths = [f for f in glob.glob(glob_path)]

        if len(file_paths) == 0:
            return None

        file_path = file_paths[0]
        if len(file_paths) > 1:
            logging.warning(f"Found multiple project conf files. Using {file_path}")

        module = DatasetModuleLoader("proj_conf", file_path).load()
        module.name = file_paths
        return cast(ProjectConfigModule, module)

    def __parse_gen_confs(self) -> List[GenerationConfigModule] | None:
        glob_path = path.join(self.root, f"**.{GEN_CONF_FILE_EXT}")
        file_paths = [f for f in glob.glob(glob_path)]

        for file_path in file_paths:
            module = DatasetModuleLoader("gen_conf", file_path).load()
            yield cast(GenerationConfigModule, module)

    def execution_order(self):
        dig = nx.DiGraph()
        execution_order = self.tables.items()
        for key, table in execution_order:
            if not table["table_def"]["gen"]["rels"]:
                dig.add_node(key)
            for dep in table["table_def"]["gen"]["rels"]:
                dig.add_edge(dep, key)

        cycles = list(nx.simple_cycles(dig))
        assert len(cycles) == 0, inspect.cleandoc(
            f"""
        Found cyclic dependencies! Ensure there are no cyclic relation in table definitions.
        {cycles}"""
        )

        return list(nx.topological_sort(dig))

    @staticmethod
    def get_table_namespace(r: str, p: str) -> List[str]:
        namespace = p.replace(r, "").replace(TABLE_DEF_FILE_EXTENSION, "").strip(sep)
        assert namespace.count(sep) == 1, inspect.cleandoc(
            f"""
        Can not extract schema and table name! File depth is not valid: "file://{p}"
        Ensure file depth is exactly one to provide schema/table namespace format."""
        )
        return namespace.split(sep)

    @staticmethod
    def get_table_def(table_path: str) -> TableDefinition:
        with open(table_path) as table_def_file:
            try:
                table_def: TableDefinition = json.load(table_def_file)
            except json.JSONDecodeError as err:
                print(
                    inspect.cleandoc(
                        f"""
                Error occurred when trying to parse table definition: "file://{table_path}"
                FIX: Ensure JSON file is formatted correctly."""
                    )
                )
                raise err

        assert "cols" in table_def, inspect.cleandoc(
            f"""
        Table definition file format is not valid: "file://{table_path}"
        Table definition does not have "cols" property.
        FIX: Add "cols" property that defines table column names to "file://{table_path}".
        EXAMPLE:
        {json.dumps({"cols": ["col1", "col2", "..."], "gen": {"...": "..."}}, indent=2)}"""
        )
        assert "gen" in table_def, inspect.cleandoc(
            f"""
        Table definition file format is not valid: "file://{table_path}"
        Table definition does not have "gen" property.
        FIX: Add "gen" property that defines generation config to "file://{table_path}".
        EXAMPLE:
        {json.dumps({"cols": ["..."], "gen": {"...": "..."}}, indent=2)}"""
        )
        assert "type" in table_def["gen"], inspect.cleandoc(
            f"""
        Table definition file format is not valid: "file://{table_path}"
        Table definition generation properties does not have "type" property.
        FIX: Add "type" property that defines generation type to "file://{table_path}".
        EXAMPLE:
        {json.dumps({"cols": ["..."], "gen": {"type": "simple", "...": "..."}}, indent=2)}"""
        )

        # "rels" property is optional, do not assert, initialize with default value
        if "rels" not in table_def["gen"]:
            table_def["gen"]["rels"] = []

        # add "mul" property to "rels" if target is a table
        if table_def["gen"]["type"] == "product" and isinstance(
            table_def["gen"]["mul"], str
        ):
            if table_def["gen"]["mul"] not in table_def["gen"]["rels"]:
                table_def["gen"]["rels"].append(table_def["gen"]["mul"])
        return table_def

    @staticmethod
    def get_table_gen(table_name: str, table_path: str) -> Any:
        gen_file_path = table_path.replace(
            TABLE_DEF_FILE_EXTENSION, TABLE_GEN_FILE_EXTENSION
        )
        assert path.isfile(gen_file_path), inspect.cleandoc(
            f"""
        Can not find generation file for table definition: "file://{table_path}"
        Ensure every table definition file has a generation file on same path.
        FIX: Create generation file at "file://{gen_file_path}"."""
        )

        try:
            mod_name = ".".join(["lokii_gen", table_name])
            spec = spec_from_file_location(mod_name, gen_file_path)
            mod = module_from_spec(spec)
            sys.modules[table_name] = mod
            spec.loader.exec_module(mod)
            table_gen = mod.gen
        except Exception as err:
            print(
                inspect.cleandoc(
                    f"""
            Error occurred when trying to parse table definition: "file://{table_path}"
            FIX: Ensure JSON file is formatted correctly."""
                )
            )
            raise err
        return table_gen


if __name__ == "__main__":
    reader = DatasetConfigParser(path.abspath("../../example/classicmodels"))
    reader.prepare()
    print(reader.execution_order())
