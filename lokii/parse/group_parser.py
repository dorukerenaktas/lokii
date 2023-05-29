import logging
import glob
import inspect
from os import path

from lokii.config import CONFIG
from lokii.model.group_module import GroupModule
from lokii.util.module_file_loader import ModuleFileLoader
from lokii.util.perf_timer_context import PerfTimerContext

GROUP_RESOLVER = "**/*%s" % CONFIG.gen.group_ext


class GroupParser:
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
            logging.warning("No group conf file found at %s" % self.root)
        else:
            logging.info("%d group definitions parsed in %s" % (group_count, t))
        return self.groups

    def __parse_groups(self):
        """
        Finds all the groups matching the group file pattern. Loads group modules and ensures
        group module configuration is valid.

        :return: parsed and validated group modules
        :rtype: list[GroupModule]
        """
        glob_path = path.join(self.root, GROUP_RESOLVER)
        file_paths = [f for f in glob.glob(glob_path)]

        for fp in file_paths:
            loader = ModuleFileLoader(fp)
            loader.load()
            module = loader.module

            m_name = path.dirname(fp).split(path.sep)[-1]
            parsed = GroupModule(m_name)

            # ensure group configuration is valid
            AE = AssertionError
            if hasattr(module, "before"):
                if not inspect.isfunction(module.before):
                    raise AE("`before` must be function at %s" % fp)
                elif len(inspect.signature(module.before).parameters) != 1:
                    raise AE("`before` accepts only one param at %s" % fp)
                else:
                    parsed.before = module.before
            if hasattr(module, "export"):
                if not inspect.isfunction(module.export):
                    raise AE("`export` must be function at %s" % fp)
                elif len(inspect.signature(module.export).parameters) != 1:
                    raise AE("`export` accepts only one param at %s" % fp)
                else:
                    parsed.export = module.export
            if hasattr(module, "after"):
                if not inspect.isfunction(module.after):
                    raise AE("`after` must be function at %s" % fp)
                elif len(inspect.signature(module.after).parameters) != 1:
                    raise AE("`after` accepts only one param at %s" % fp)
                else:
                    parsed.after = module.after

            yield parsed
