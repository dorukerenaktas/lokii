import csv
import shutil
from itertools import groupby
from pathlib import Path

from lokii import Lokii
import unittest

DATA_FOLDER = 'data'


class TestLokii(unittest.TestCase):

    def setUp(self) -> None:
        """
        Before running each test remove data directory if exists
        """
        data_path = Path(DATA_FOLDER)
        if data_path.exists() and data_path.is_dir():
            shutil.rmtree(data_path)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        After all tests are finished remove data directory
        """
        data_path = Path(DATA_FOLDER)
        if data_path.exists() and data_path.is_dir():
            shutil.rmtree(data_path)

    def test_simple_table_should_generate_expected_rows(self):
        """
        Test simple table generation.
        """
        simple_count = 100
        lokii = Lokii(out_folder=DATA_FOLDER, silent=True)

        def col_func(x):
            return x * x

        col_const = 'constant_column'

        simple_table = lokii.table('test_simple') \
            .cols('id', 'col_func', 'col_const') \
            .simple(simple_count, lambda i, r: {
                'id': i,
                'col_func': col_func(i),
                'col_const': col_const,
            })
        lokii.generate()

        # Confirm that lokii generates simple table
        with open(simple_table.outfile) as csv_file:
            simple_rows = list(csv.DictReader(csv_file, delimiter=','))

            # Confirm that correct amount of rows are generated
            self.assertEqual(len(simple_rows), simple_count)
            # Confirm that the generated ids are starting from 1
            self.assertEqual(simple_rows[0]['id'], str(1))
            # Confirm that the generated ids end at count
            self.assertEqual(simple_rows[simple_count - 1]['id'], str(simple_count))

            an_index = int(simple_count / 2)
            # Confirm that the generated row yields result of defined function
            self.assertEqual(simple_rows[an_index]['col_func'], str(col_func(an_index + 1)))
            # Confirm that the generated row yields constant
            self.assertEqual(simple_rows[an_index]['col_const'], str(col_const))

    def test_relation_table_should_generate_expected_rows(self):
        """
        Test relation table generation.
        """
        simple_count = 100
        rel_count = 200
        lokii = Lokii(out_folder=DATA_FOLDER, silent=True)

        simple_table = lokii.table('test_simple') \
            .cols('id', 'col') \
            .simple(simple_count, lambda i, r: {
                'id': i,
                'col': 'col',
            })

        rel_table = lokii.table('test_rel') \
            .cols('id', 'rel_id') \
            .rels(simple_table) \
            .simple(rel_count, lambda i, r: {
                'id': i,
                'rel_id': r['test_simple']['id']
            })

        lokii.generate()

        # Confirm that lokii generates relation table
        with open(rel_table.outfile) as csv_file:
            rel_rows = list(csv.DictReader(csv_file, delimiter=','))

            # Confirm that correct amount of rows are generated
            self.assertEqual(len(rel_rows), rel_count)
            # Confirm that the generated ids are starting from 1
            self.assertEqual(rel_rows[0]['id'], str(1))
            # Confirm that the generated ids end at count
            self.assertEqual(rel_rows[rel_count - 1]['id'], str(rel_count))

            # Confirm that all generated rows contains valid relation id
            for row in rel_rows:
                self.assertTrue(1 <= int(row['rel_id']) <= simple_count)

    def test_product_table_should_generate_expected_rows(self):
        """
        Test product table generation.
        """
        simple_count = 100
        lokii = Lokii(out_folder=DATA_FOLDER, silent=True)

        simple_table = lokii.table('test_simple') \
            .cols('id', 'col') \
            .simple(simple_count, lambda i, r: {
                'id': i,
                'col': 'col',
            })

        multiplier = [1, 2, 3]
        product_table = lokii.table('test_product') \
            .cols('id', 'multiplicand_id', 'multiplier') \
            .multiply(simple_table, lambda i, m, r: {
                'id': i,
                'multiplicand_id': r['test_simple']['id'],
                'multiplier': m
            }, multiplier)

        lokii.generate()

        # Confirm that lokii generates product table
        with open(product_table.outfile) as csv_file:
            product_rows = list(csv.DictReader(csv_file, delimiter=','))

            # Confirm that correct amount of rows are generated
            self.assertEqual(len(product_rows), simple_count * len(multiplier))

            sorted_rows = sorted(product_rows, key=lambda r: r['multiplicand_id'])
            grouped_rows = [list(it) for k, it in groupby(sorted_rows, lambda r: r['multiplicand_id'])]
            for rows in grouped_rows:
                # Confirm that all multiplied rows of simple table has multiplied by all multiplier items
                self.assertEqual(sorted([int(r['multiplier']) for r in rows]), sorted(multiplier))

    def test_table_should_not_write_none_rows(self):
        """
        Test product table generation.
        """
        simple_count = 100
        rel_count = 100
        lokii = Lokii(out_folder=DATA_FOLDER, silent=True)

        simple_table = lokii.table('test_simple') \
            .cols('id', 'col') \
            .simple(simple_count, lambda i, r: {
                'id': i,
                'col': 'col',
            } if i < int(simple_count / 2) + 1 else None)

        rel_table = lokii.table('test_rel') \
            .cols('id', 'col') \
            .simple(simple_count, lambda i, r: {
                'id': i,
                'col': 'col',
            } if i < int(rel_count / 2) + 1 else None)

        multiplier = [1, 2, 3]
        product_table = lokii.table('test_product') \
            .cols('id', 'rel_id', 'multiplicand_id', 'multiplier') \
            .rels(rel_table) \
            .multiply(simple_table, lambda i, m, r: {
                'id': i,
                'rel_id': r['test_rel']['id'],
                'multiplicand_id': r['test_simple']['id'],
                'multiplier': m
            }, multiplier)

        lokii.generate()

        # Confirm that lokii not writes none rows
        with open(simple_table.outfile) as csv_file:
            simple_rows = list(csv.DictReader(csv_file, delimiter=','))

            # Confirm that correct amount of rows are generated
            self.assertEqual(len(simple_rows), int(simple_count / 2))

        # Confirm that lokii generates product table
        with open(product_table.outfile) as csv_file:
            product_rows = list(csv.DictReader(csv_file, delimiter=','))

            # Confirm that correct amount of rows are generated
            self.assertEqual(len(product_rows), int(simple_count / 2) * len(multiplier))

    def test_table_should_write_default_rows(self):
        """
        Test product table generation.
        """
        simple_count = 100
        lokii = Lokii(out_folder=DATA_FOLDER, silent=True)

        default_rows = [
                {'id': 1, 'col': 1},
                {'id': 2, 'col': 2},
                {'id': 3, 'col': 3}
            ]

        simple_table = lokii.table('test_simple') \
            .cols('id', 'col') \
            .defs(default_rows) \
            .simple(simple_count, lambda i, r: {
                'id': i,
                'col': 'col',
            } if i < int(simple_count / 2) + 1 else None)

        lokii.generate()

        # Confirm that lokii not writes none rows
        with open(simple_table.outfile) as csv_file:
            simple_rows = list(csv.DictReader(csv_file, delimiter=','))

            # Confirm that correct amount of rows are generated
            self.assertEqual(len(simple_rows), int(simple_count / 2))

            # Confirm that default rows are generated
            for index, default in enumerate(default_rows):
                self.assertEqual(str(simple_rows[index]['col']), str(default['col']))
