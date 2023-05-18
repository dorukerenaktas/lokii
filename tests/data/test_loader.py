import inspect
import unittest
from unittest import mock
from unittest.mock import MagicMock

from data.loader import DatasetModuleLoader


class TestDatasetModuleLoader(unittest.TestCase):
    @mock.patch("os.path.exists", MagicMock(return_value=False))
    def test_load_raise_error_if_file_not_found(self):
        loader = DatasetModuleLoader("proj_conf", "/test/path/proj.conf.py")
        self.assertRaises(FileNotFoundError, loader.load)

    @mock.patch("os.path.exists", MagicMock(return_value=True))
    @mock.patch("importlib.machinery.SourceFileLoader.get_code")
    def test_load_should_exec_loaded_module(self, m_get_code):
        m_get_code.return_value = compile(
            'conf = {"test_env": {}}',
            "/test/path/proj.conf.py",
            "exec",
        )
        loader = DatasetModuleLoader("proj_conf", "/test/path/proj.conf.py")
        module = loader.load()
        self.assertEqual(module.name, "proj")
        self.assertEqual(module.conf, {"test_env": {}})
