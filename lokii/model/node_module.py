from typing import TypedDict, Callable

GenFunc = Callable[[dict], dict]

GenRunConf = TypedDict(
    "GenRunConf", {"source": str, "wait": list[str], "func": Callable}
)


class GenNodeModule:
    """
    Module specification that defines node generation configuration.

    :var runs: Generation run configurations of the node
    :type runs: list[GenRunConf]
    :var name: Name of the node
    :type name: str
    :var version: Code version of the node
    :type version: str
    :var groups: Groups that the node belongs
    :type groups: list[str]
    """

    def __init__(
        self,
        runs: list[GenRunConf],
        name: str = None,
        version: str = None,
        groups: list[str] = None,
    ):
        self.runs = runs
        self.name = name
        self.version = version
        self.groups = groups or []


class GenRun:
    def __init__(self, node_name: str, version: str, index: int, run_conf: GenRunConf):
        self.node_name = node_name
        self.node_version = version
        self.run_order = index
        self.run_key = GenRun.create_key(node_name, index)

        self.source = run_conf["source"]
        self.func = run_conf["func"]
        self.wait = []
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
