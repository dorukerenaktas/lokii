from typing import Callable

ExportFunc = Callable[[dict], None]


class GroupModule:
    """
    Module specification that defines node group export configuration.

    :var before: Called once before export function
    :type before: ExportFunc
    :var after: Called once after export function
    :type after: ExportFunc
    :var export: Called for every node in this group
    :type export: ExportFunc
    :var name: Name of the group
    :type name: str
    :var groups: Groups that the node belongs
    :type groups: list[str]
    """

    def __init__(self, name, groups=None):
        """
        Initialize generation node group module.
        :param name: name of the group
        :type name: str
        :param groups: export groups of the node
        :type groups: list[str]
        """
        self.name = name
        self.groups = groups or []
        self.before = None
        self.after = None
        self.export = None
