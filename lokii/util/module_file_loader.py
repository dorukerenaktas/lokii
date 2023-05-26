from __future__ import annotations

import os
import sys
import hashlib
import inspect
from types import ModuleType
from importlib.util import spec_from_file_location, module_from_spec


class ModuleFileLoader:
    def __init__(self, file_path: str):
        """
        Loads module from given path.

        :param file_path: file path of the module
        """
        self.path = os.path.abspath(file_path)
        self.filename = os.path.basename(file_path)

        self.module: ModuleType | None = None
        self.version: str | None = None

    def load(self) -> None:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"No module file found at: {self.path}")

        # read file spec from given path. filename is used as module name
        spec = spec_from_file_location(self.filename, self.path)
        module = module_from_spec(spec)

        # introduce module to system
        sys.modules[self.filename] = module
        spec.loader.exec_module(module)
        self.module = module

        # acquire module source code as str
        src = inspect.getsource(module).encode("utf-8")
        h = hashlib.blake2b(digest_size=20)
        h.update(src)

        # hash source code to detect changes
        self.version = h.hexdigest()
