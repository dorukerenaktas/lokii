from lokii import Lokii
import unittest


class TestTableGeneration(unittest.TestCase):

    def test_pass(self):
        lokii = Lokii()

        user_table = lokii.table('common.user') \
            .cols('id', 'name', 'surname') \
            .simple(30000, lambda i, _: {
                'id': i,
            })
