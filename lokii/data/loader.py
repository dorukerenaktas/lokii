from __future__ import annotations

import sys
from os import path
from types import ModuleType
from typing import Literal
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_file_location, module_from_spec

from model.proj_conf import ProjConf

DatasetModuleTypes = Literal["proj_conf", "gen_conf"]


class DatasetModuleLoader:
    def __init__(self, file_type: DatasetModuleTypes, file_path: str):
        """
        Loads special project module from given path.

        :type file_type: module type for structure checks
        :param file_path: file path of the dataset generation function or config
        """
        self.type = file_type
        self.path = path.abspath(file_path)
        self.filename = path.basename(file_path)

        self.spec: ModuleSpec | None = None
        self.module: ModuleType | None = None

    def load(self) -> ModuleType:
        if not path.exists(self.path):
            raise FileNotFoundError(f"No {self.type} file found at: {self.path}")

        module_name = ".".join([self.type, self.filename])
        self.spec = spec_from_file_location(module_name, self.path)
        self.module = module_from_spec(self.spec)

        sys.modules[module_name] = self.module
        self.spec.loader.exec_module(self.module)

        if self.type == "proj_conf":
            project_name = self.filename.split(".")[0]
            self.module.name = project_name
            self._check_proj_conf_module()
        if self.type == "gen_conf":
            self._check_gen_conf_module()
        return self.module

    def _check_proj_conf_module(self) -> None:
        if self.module.conf:
            if not isinstance(self.module.conf, dict):
                raise AssertionError("Provided `conf` is not a dict!")

            for env, conf in self.module.conf.items():
                self.__check_proj_conf(env, conf)
        pass

    def __check_proj_conf(self, env: str, conf: ProjConf) -> None:
        if not isinstance(conf, dict):
            raise AssertionError(f"Provided `conf.{env}` is not a dict!")
        if "schema_dept" in conf and not isinstance(conf["schema_dept"], int):
            raise AssertionError(f"Provided `conf.{env}.schema_dept` is not a int!")

    def _check_gen_conf_module(self) -> None:
        pass
