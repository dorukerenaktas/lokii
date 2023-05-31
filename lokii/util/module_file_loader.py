import os
import sys
import hashlib
import inspect
from types import ModuleType


class ModuleFileLoader:
    """
    :type module: ModuleType or None
    :type version: str or None
    """

    def __init__(self, file_path: str):
        """
        Loads module from given path.

        :param file_path: file path of the module
        """
        self.path = os.path.abspath(file_path)
        self.filename = os.path.basename(file_path)

        self.module = None
        self.version = None

    def load(self) -> None:
        if not os.path.exists(self.path):
            raise FileNotFoundError("No module file found at: %s" % self.path)

        try:
            import importlib.util

            # read file spec from given path. filename is used as module name
            spec = importlib.util.spec_from_file_location(self.filename, self.path)
            module = importlib.util.module_from_spec(spec)

            # introduce module to system
            sys.modules[self.filename] = module
            spec.loader.exec_module(module)
            self.module = module
        except ImportError:
            from imp import load_source

            module = load_source(self.filename, self.path)

        # acquire module source code as str
        src = inspect.getsource(module).encode("utf-8")
        h = hashlib.blake2b(digest_size=20)
        h.update(src)

        # hash source code to detect changes
        self.version = h.hexdigest()
