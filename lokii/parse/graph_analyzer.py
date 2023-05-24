import networkx as nx

from lokii.model.gen_module import GenRun


class GraphAnalyzer:
    def __init__(self, gen_runs: list[GenRun]):
        """
        Reads and validates dataset configuration from filesystem structure.

        :param gen_runs: root path of the dataset generation schema
        """
        self.gen_runs = gen_runs

        # initialize directed graph
        self.run_dig = nx.DiGraph()
        for run in self.gen_runs:
            if not run.wait:
                self.run_dig.add_node(run.run_key)
            for dep in run.wait:
                self.run_dig.add_edge(dep, run.run_key)

    def dependencies(self, run_key: str) -> list[str]:
        return list(nx.ancestors(self.run_dig, run_key))

    def execution_order(self) -> list[str]:
        cycles = list(nx.simple_cycles(self.run_dig))
        if len(cycles) != 0:
            raise AssertionError(f"Found cyclic dependencies!\n{cycles}")
        return list(nx.topological_sort(self.run_dig))
