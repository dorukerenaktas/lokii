import pytest
from typing import Any

from lokii.util.module_file_loader import ModuleFileLoader


@pytest.fixture
def mock_source_file_loader(mocker):
    def patch(exists: bool = False, code: Any = "") -> None:
        mocker.patch("os.path.exists", return_value=exists)
        mocker.patch("inspect.getsource", return_value="string code content")
        mocker.patch(
            "importlib.machinery.SourceFileLoader.get_code", lambda *args: code
        ),

    return patch


def test_load_raise_error_if_file_not_found(mock_source_file_loader):
    mock_source_file_loader(False)
    loader = ModuleFileLoader("/test/path/any.py")
    with pytest.raises(FileNotFoundError):
        loader.load()


def test_load_should_exec_loaded_module(mock_source_file_loader):
    code = 'conf = {"test_env": {}}'
    mock_source_file_loader(True, compile(code, "/test/path/any.py", "exec"))
    loader = ModuleFileLoader("/test/path/any.py")
    loader.load()
    assert loader.module.conf == {"test_env": {}}
