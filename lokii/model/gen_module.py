from __future__ import annotations

from typing import TypedDict, List, Optional, Callable, Dict

GenFunc = Callable[[Dict], Dict]


class GenRunConf(TypedDict):
    """
    :var source: Source SQL statement
    """

    source: Optional[str]
    wait: Optional[List[str]]
    rels: Optional[Dict[str, str]]
    func: Callable[[Dict], Dict]


class GenNodeModule:
    name: Optional[str]
    runs: List[GenRunConf]


class GenRun:
    def __init__(self, node_name: str, index: int, run_conf: GenRunConf):
        self.node_name = node_name
        self.run_order = index
        self.run_key = GenRun.create_key(node_name, index)

        self.source = run_conf["source"]
        self.wait = []
        self.rels = run_conf["rels"]
        self.func = run_conf["func"]

        if index > 0:
            self.wait.append(GenRun.create_key(node_name, index - 1))
        for dep in run_conf["wait"]:
            self.wait.append(dep if GenRun.is_key(dep) else GenRun.create_key(dep, 0))

    @staticmethod
    def create_key(node_name: str, index: int) -> str:
        return "/".join([node_name, str(index)])

    @staticmethod
    def is_key(run_key: str) -> bool:
        return "/" in run_key
