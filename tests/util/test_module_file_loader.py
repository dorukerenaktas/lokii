import pytest
from unittest import mock

from util.module_file_loader import ModuleFileLoader


@mock.patch("os.path.exists", lambda *args: False)
def test_load_raise_error_if_file_not_found():
    loader = ModuleFileLoader("/test/path/any.py")
    with pytest.raises(FileNotFoundError):
        loader.load()


@mock.patch("os.path.exists", lambda *args: True)
@mock.patch("importlib.machinery.SourceFileLoader.get_code")
def test_load_should_exec_loaded_module(m_get_code):
    m_get_code.return_value = compile(
        'conf = {"test_env": {}}',
        "/test/path/any.py",
        "exec",
    )
    loader = ModuleFileLoader("/test/path/any.py")
    module = loader.load()
    assert module.conf == {"test_env": {}}
