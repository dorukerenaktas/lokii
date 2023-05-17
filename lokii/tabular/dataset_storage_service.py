from __future__ import annotations

import pickle
from typing import Literal

from faker import Faker
from pathos.pools import ParallelPool

from model.execution_config import ExecutionConfig
from model.fake_data_config import FakeDataConfig

from model.table_definition import DatasetTableDefinition


class DatasetStorageService:
    def __init__(self):
        """
        Generates dataset according to given configuration.
        """
        self.__generated_tables = []

    def save(self, table_config):
        self.__generated_tables.append(table_config)

    def query(self, table_config):
        self.__generated_tables.append(table_config)
