import glob
import inspect
import json
import networkx as nx
from os import path, sep

from typing import Dict, List

TABLE_DEF_FILE_EXTENSION = '.json'
TABLE_GEN_FILE_EXTENSION = '.py'


class TabularDataset:
    def __init__(self, root_path: str):
        """
        Database table like data structure definition that hold column and general configuration to
        adjust generated data.

        :param root_path: source path of the tabular schema structure
        """
        self.root = root_path
        self.tables: Dict[str, Dict] = {}

    def prepare(self):
        # read all table definitions from given path
        glob_path = path.join(self.root, f"**/*{TABLE_DEF_FILE_EXTENSION}")
        file_paths = [f for f in glob.iglob(glob_path)]

        tables = {}
        for p in file_paths:
            [table_schema, table_name] = TabularDataset.get_table_namespace(self.root, p)
            table_def = TabularDataset.get_table_def(p)
            table_gen = TabularDataset.get_table_gen(p)

            table_namespace = f"{table_schema}.{table_name}"
            tables[table_namespace] = {
                "table_schema": table_schema,
                "table_name": table_name,
                "table_def": table_def,
                "table_gen": table_gen
            }
        self.tables = tables

    def execution_order(self):
        dig = nx.DiGraph()
        execution_order = self.tables.items()
        for (key, table) in execution_order:
            if not table['table_def']['gen']['rels']:
                dig.add_node(key)
            for dep in table['table_def']['gen']['rels']:
                dig.add_edge(dep, key)

        cycles = list(nx.simple_cycles(dig))
        assert len(cycles) == 0, inspect.cleandoc(f"""
        Found cyclic dependencies! Ensure there are no cyclic relation in table definitions.
        {cycles}""")

        return list(nx.topological_sort(dig))

    @staticmethod
    def get_table_namespace(r: str, p: str) -> List[str]:
        namespace = p.replace(r, "").replace(TABLE_DEF_FILE_EXTENSION, "").strip(sep)
        assert namespace.count(sep) == 1, inspect.cleandoc(f"""
        Can not extract schema and table name! File depth is not valid: "file://{p}"
        Ensure file depth is exactly one to provide schema/table namespace format.""")
        return namespace.split(sep)

    @staticmethod
    def get_table_def(p: str) -> Dict:
        with open(p) as table_def_file:
            try:
                table_def = json.load(table_def_file)
            except json.JSONDecodeError as err:
                print(inspect.cleandoc(f"""
                Error occurred when trying to parse table definition: "file://{p}"
                FIX: Ensure JSON file is formatted correctly."""))
                raise err

        assert "cols" in table_def, inspect.cleandoc(f"""
        Table definition file format is not valid: "file://{p}"
        Table definition does not have "cols" property.
        FIX: Add "cols" property that defines table column names to "file://{p}".
        EXAMPLE:
        {json.dumps({"cols": ["col1", "col2", "..."], "gen": {"...": "..."}}, indent=2)}""")
        assert "gen" in table_def, inspect.cleandoc(f"""
        Table definition file format is not valid: "file://{p}"
        Table definition does not have "gen" property.
        FIX: Add "gen" property that defines generation config to "file://{p}".
        EXAMPLE:
        {json.dumps({"cols": ["..."], "gen": {"...": "..."}}, indent=2)}""")
        assert "type" in table_def["gen"], inspect.cleandoc(f"""
        Table definition file format is not valid: "file://{p}"
        Table definition generation properties does not have "type" property.
        FIX: Add "type" property that defines generation type to "file://{p}".
        EXAMPLE:
        {json.dumps({"cols": ["..."], "gen": {"type": "simple", "...": "..."}}, indent=2)}""")

        # "rels" property is optional, do not assert, initialize with default value
        if "rels" not in table_def["gen"]:
            table_def["gen"]["rels"] = []

        # add "mul" property to "rels" if target is a table
        if table_def["gen"]["type"] == "multiply" and isinstance(table_def["gen"]["mul"], str):
            if table_def["gen"]["mul"] not in table_def["gen"]["rels"]:
                table_def["gen"]["rels"].append(table_def["gen"]["mul"])
        return table_def

    @staticmethod
    def get_table_gen(p: str):
        gen_file_path = p.replace(TABLE_DEF_FILE_EXTENSION, TABLE_GEN_FILE_EXTENSION)
        assert path.isfile(gen_file_path), inspect.cleandoc(f"""
        Can not find generation file for table definition: "file://{p}"
        Ensure every table definition file has a generation file on same path.
        FIX: Create generation file at "file://{gen_file_path}".""")

        with open(gen_file_path) as table_gen_file:
            try:
                table_gen = compile(table_gen_file.read(), gen_file_path, 'exec')
            except Exception as err:
                print(inspect.cleandoc(f"""
                Error occurred when trying to parse table definition: "file://{p}"
                FIX: Ensure JSON file is formatted correctly."""))
                raise err
        return table_gen


if __name__ == "__main__":
    tabular = TabularDataset("/home/doruk/Documents/Projects/thor/Database/scripts/schemas")
    tabular.prepare()
