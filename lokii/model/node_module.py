from typing import Callable

GenItemFunc = Callable[[dict], dict]


class GenNodeModule:
    """
    Module specification that defines node generation configuration.

    :var source: source query to create items
    :type source: str
    :var item: item generation function
    :type item: GenFunc
    :var name: Name of the node
    :type name: str
    :var version: Code version of the node
    :type version: str
    :var groups: Groups that the node belongs
    :type groups: list[str]
    """

    def __init__(self, source, item, name=None, version=None, groups=None):
        """
        Initialize generation node module.
        :param source: source query to create items
        :type source: str
        :param item: item generation function
        :type item: GenFunc
        :param name: name of the node
        :type name: str
        :param groups: export groups of the node
        :type groups: list[str]
        """
        self.source = source
        self.item = item
        self.name = name
        self.version = version
        self.groups = groups or []
