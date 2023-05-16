from faker import Faker

from model.fake_config import FakeConfig
from model.table_config import TableConfig


class TabularDataset:
    def __init__(self, table_config: TableConfig, fake_config: FakeConfig):
        """
        Database table like data structure definition that hold column and general configuration to
        adjust generated data.

        :param table_config: source path of the tabular schema structure
        :param fake_config: source path of the tabular schema structure
        """
        self.table_config = table_config
        self.fakes = {[lang]: Faker([lang]) for lang in fake_config["langs"]}
