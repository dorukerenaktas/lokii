import csv
import json
from os import path, PathLike
from typing import Union

from faker import Faker

from .config import LokiConfig
from .table import Table


def get_table_path(out_folder: str, name: str):
    if '/' in name:
        [schema_name, table_name] = name.split('/')
        return path.join(out_folder, schema_name, table_name + '.csv')
    return path.join(out_folder, name + '.csv')


def get_table(out_folder: str, name: str):
    with open(get_table_path(out_folder, name), newline='\n', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter=',', quotechar='"')
        headers = next(reader)
        rows = []
        for row in reader:
            rows.append({key: value for key, value in zip(headers, row)})
        return rows


class Lokii:
    @staticmethod
    def from_file(config_file: Union[str, bytes, PathLike], out_folder: Union[str, bytes, PathLike]='./out'):
        with open(config_file) as config_file:
            config = json.load(config_file)
        return Lokii(config, out_folder)

    def __init__(self, config: LokiConfig, out_folder: Union[str, bytes, PathLike]='./out'):
        self.config = config
        self.out_folder = out_folder

    def generate(self):
        fakes = {}
        for lang in self.config['languages']:
            fakes[lang] = Faker([lang])

        for table_data in self.config['tables']:
            table = Table(table_data, fakes)
            table_file_name = get_table_path(self.out_folder, table_data['name'])
            with open(table_file_name, 'w+', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=[name for name in table_data['cols']])
                writer.writeheader()

                def get_table_with_path(name: str):
                    return get_table(self.out_folder, name)

                table.exec(writer, get_table_with_path)
