import random
from csv import DictWriter
from typing import Dict, Callable, Collection

from faker import Faker

from ..config import TableConfig
from .row import Row


class Table:
    def __init__(self, config: TableConfig, fakes: Dict[str, Faker], default_lang: str = 'en'):
        self.option = config['option']
        self.row = Row(config['name'], config['cols'])
        self.default = config['default'] if 'default' in config else []
        if self.option['index_start']:
            self.index = len(self.default) + self.option['index_start']
        else:
            self.index = len(self.default)
        self.default_lang = default_lang
        self.fakes = fakes

    def exec(self, writer: DictWriter, get_rel: Callable[[str], Collection[Dict]]):
        # Write default rows
        for row in self.default:
            writer.writerow(row)

        if self.option['type'] == 'simple':
            self.simple(writer)

        if self.option['type'] == 'multiply':
            self.multiply(writer, get_rel)

        if self.option['type'] == 'relation':
            self.relation(writer, get_rel)

    def simple(self, writer: DictWriter):
        for i in range(1, self.option['args']['count'] + 1):
            self.index += 1
            writer.writerow(
                self.row.exec(self.index, self.default_lang, self.fakes[self.default_lang], None))

    def multiply(self, writer: DictWriter, get_rel: Callable[[str], Collection[Dict]]):
        rel_rows = get_rel(self.option['args']['table'])
        if 'where' in self.option['args']:
            rel_rows = self.get_valid_rows(rel_rows, self.option['args']['where'])
        for row in rel_rows:
            if 'var' in self.option['args'] and random.random() < self.option['args']['var']:
                continue

            rel = {self.option['args']['table']: row}
            for i in range(self.option['args']['count']):
                self.index += 1

                selected_lang = self.default_lang
                if 'languages' in self.option['args']:
                    selected_lang = self.option['args']['languages'][i]
                writer.writerow(
                    self.row.exec(self.index, selected_lang, self.fakes[selected_lang], rel))

    def relation(self, writer: DictWriter, get_rel: Callable[[str], Collection[Dict]]):
        left_rel_rows = get_rel(self.option['args']['left']['table'])
        if 'where' in self.option['args']['left']:
            left_rel_rows = self.get_valid_rows(left_rel_rows, self.option['args']['left']['where'])

        right_rel_rows = get_rel(self.option['args']['right']['table'])
        if 'where' in self.option['args']['right']:
            right_rel_rows = self.get_valid_rows(right_rel_rows,
                                                 self.option['args']['right']['where'])

        if self.option['args']['count'] == 'cover':
            for row in left_rel_rows:
                right_row = random.choice(right_rel_rows)
                self.index += 1

                rel = {
                    self.option['args']['left']['table']: row,
                    self.option['args']['right']['table']: right_row
                }
                writer.writerow(
                    self.row.exec(self.index, self.default_lang, self.fakes[self.default_lang],
                                  rel))
        else:
            for i in range(self.option['args']['count']):
                left_row = random.choice(left_rel_rows)
                right_row = random.choice(right_rel_rows)
                self.index += 1

                rel = {
                    self.option['args']['left']['table']: left_row,
                    self.option['args']['right']['table']: right_row
                }
                writer.writerow(
                    self.row.exec(self.index, self.default_lang, self.fakes[self.default_lang],
                                  rel))

    @staticmethod
    def get_valid_rows(rel_rows: Collection, conds: Collection):
        valid_rows = []
        for target in rel_rows:
            eligible = True
            for cond in conds:
                for key in cond:
                    if target[key] != cond[key]:
                        eligible = False
            if eligible:
                valid_rows.append(target)
        return valid_rows
