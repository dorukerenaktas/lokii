from __future__ import annotations

import sys
from os import path
from types import ModuleType
from importlib.util import spec_from_file_location, module_from_spec


class ModuleFileLoader:
    def __init__(self, file_path: str):
        """
        Loads module from given path.

        :param file_path: file path of the module
        """
        self.path = path.abspath(file_path)
        self.filename = path.basename(file_path)

    def load(self) -> ModuleType:
        if not path.exists(self.path):
            raise FileNotFoundError(f"No module file found at: {self.path}")

        spec = spec_from_file_location(self.filename, self.path)
        module = module_from_spec(spec)

        sys.modules[self.filename] = module
        spec.loader.exec_module(module)

        return module
