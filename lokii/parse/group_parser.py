import logging
from os import path
from glob import glob

from lokii.config import CONFIG
from lokii.model.group_module import GroupModule
from lokii.util.module_file_loader import ModuleFileLoader
from lokii.util.perf_timer_context import PerfTimerContext
from lokii.parse.base_parser import BaseParser

logger = logging.getLogger("lokii.group_parser")
GROUP_RESOLVER = "**/*%s" % CONFIG.gen.group_ext


class GroupParser(BaseParser):
    """
    Reads and validates group export configurations from filesystem structure.

    :var groups: parsed group modules
    :type groups: dict[str, GroupModule]
    """

    def __init__(self, source_folder):
        """
        Initializes parser.
        :param source_folder: root path of the project
        :type source_folder: str
        """
        self.root = source_folder
        self.groups = {}

    def parse(self):
        """
        :return: parsed and validated node run flat map
        :rtype: dict[str, GroupModule]
        """
        with PerfTimerContext() as t:
            groups = list(self.__parse_groups())
            self.groups = {n.name: n for n in groups}

        group_count = len(groups)
        if group_count == 0:
            logger.warning("No group conf file found", extra={"at": self.root})
        else:
            logger.info("%d group definitions parsed in %s" % (group_count, t))
        return self.groups

    def __parse_groups(self):
        """
        Finds all the groups matching the group file pattern. Loads group modules and ensures
        group module configuration is valid.

        :return: parsed and validated group modules
        :rtype: list[GroupModule]
        """
        glob_path = path.join(self.root, GROUP_RESOLVER)
        file_paths = [f for f in glob(glob_path, recursive=True)]

        for fp in file_paths:
            loader = ModuleFileLoader(fp)
            loader.load()
            mod = loader.module

            # extract group name from dir name
            m_name = path.dirname(fp).split(path.sep)[-1]
            # extract groups from file path
            m_groups = path.relpath(path.dirname(fp), self.root).split(path.sep)[:-1]
            parsed = GroupModule(m_name, m_groups)
            logger.debug("Found valid group `%s`", m_name, extra={"at": fp})

            # ensure group configuration is valid
            if self.attr(mod, "before"):
                self.func(mod.before, "`before` must be function at %s" % fp)
                self.sig(mod.before, 1, "`before` accepts only one param at %s" % fp)
                parsed.before = mod.before
            if self.attr(mod, "export"):
                self.func(mod.export, "`export` must be function at %s" % fp)
                self.sig(mod.export, 1, "`export` accepts only one param at %s" % fp)
                parsed.export = mod.export
            if self.attr(mod, "after"):
                self.func(mod.after, "`after` must be function at %s" % fp)
                self.sig(mod.after, 1, "`after` accepts only one param at %s" % fp)
                parsed.after = mod.after
            yield parsed
