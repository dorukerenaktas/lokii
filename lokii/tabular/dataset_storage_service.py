from __future__ import annotations


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
