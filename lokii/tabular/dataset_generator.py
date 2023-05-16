from faker import Faker

from model.fake_data_config import FakeDataConfig
from model.table_definition import TableDefinition


class DatasetGenerator:
    def __init__(self, table_config: TableDefinition, fake_config: FakeDataConfig):
        """
        Generates dataset according to given configuration.

        :param table_config: source path of the tabular schema structure
        :param fake_config: source path of the tabular schema structure
        """
        self.table_config = table_config
        self.fakes = {[lang]: Faker([lang]) for lang in fake_config["langs"]}
