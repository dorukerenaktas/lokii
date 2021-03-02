from lokii import Lokii
import unittest


class TestTable(unittest.TestCase):

    def test_cols_should_raise_error_if_count_is_not_valid(self):
        lokii = Lokii(silent=True)
        self.assertRaises(KeyError, lokii.table('test').cols, 'id')

    def test_cols_should_raise_error_if_have_duplicates(self):
        lokii = Lokii(silent=True)
        self.assertRaises(KeyError, lokii.table('test').cols, 'id', 'name', 'id')

    def test_rels_should_raise_error_if_have_duplicates(self):
        lokii = Lokii(silent=True)
        self.assertRaises(KeyError, lokii.table('test').rels, 'table1', 'table2', 'table1')
