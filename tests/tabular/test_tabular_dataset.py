import unittest
from unittest import mock

from tabular.dataset_config_reader import DatasetConfigReader

def_files = {
    '/test/root/s1/a.json': {"cols": ['a', "b"], "gen": {}},
    '/test/root/s1/b.json': {"cols": ['a', "b"], "gen": {}},
    '/test/root/s2/c.json': {"cols": ['a', "b"], "gen": {}}
}
gen_files = {
    '/test/root/s1/a.py': {"cols": ['a', "b"], "gen": {}},
    '/test/root/s1/b.py': {"cols": ['a', "b"], "gen": {}},
    '/test/root/s2/c.py': {"cols": ['a', "b"], "gen": {}}
}


def open_side_effect(name):
    return mock.mock_open(read_data=name)()


@mock.patch('tabular.tabular.glob.iglob', lambda *args: list(def_files.keys()))
@mock.patch('tabular.tabular.path.isfile', lambda *args: args[0] in gen_files)
@mock.patch('tabular.tabular.json.load', lambda *args: def_files[args[0].read()])
class TestTabular(unittest.TestCase):

    def test_prepare(self):
        with mock.patch("builtins.open", side_effect=open_side_effect):
            tabular = DatasetConfigReader('/test/root')
            tabular.prepare()
