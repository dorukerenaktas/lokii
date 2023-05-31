from typing import Callable

ExportFunc = Callable[[dict], None]


class GroupModule:
    """
    Module specification that defines node group export configuration.

    :var name: Name of the group
    :type name: str
    :var before: Called once before export function
    :type before: ExportFunc
    :var after: Called once after export function
    :type after: ExportFunc
    :var export: Called for every node in this group
    :type export: ExportFunc
    """

    name = None
    before = None
    after = None
    export = None

    def __init__(self, name):
        """
        Initialize generation node group module.
        :param name: name of the group
        :type name: str
        """
        self.name = name
