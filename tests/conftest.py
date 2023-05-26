import pytest
from unittest.mock import Mock

from lokii import Lokii


@pytest.fixture
def found_mods(mocker, request):
    gen_files = request.param or []
    gen_files = [m if ".gen.py" in m else f"{m}.gen.py" for m in gen_files]
    mocker.patch("glob.glob", return_value=gen_files)
    return gen_files


@pytest.fixture
def loaded_mods(mocker, found_mods, request):
    def module_file_loader_side_effect(file_path: str):
        mods = request.param or []
        mod_i = found_mods.index(file_path)
        if mods[mod_i].runs and isinstance(mods[mod_i].runs, list):
            mods[mod_i].runs = [
                {"source": "SELECT * FROM range(100)", "func": lambda x: x, **run}
                for run in mods[mod_i].runs
            ]
        loader = {
            "load": Mock(),
            "module": mods[mod_i],
            "version": mods[mod_i].version or "v1",
        }
        return type("ModuleFileLoader", (object,), loader or {})()

    mock = mocker.patch("lokii.parse.node_parser.ModuleFileLoader")
    mock.side_effect = module_file_loader_side_effect
    return request.param or []


@pytest.fixture
def mock_module_loader(mocker):
    def patch(files: list[str] = None, node: dict = None) -> None:
        mocker.patch("glob.glob", return_value=files or [])
        mocker.patch("inspect.getsource", return_value="string code content")
        m = type("GenNodeModule", (object,), node or {})()
        mock = mocker.patch("lokii.parse.node_parser.ModuleFileLoader")
        mock.return_value.module = m
        mock.return_value.version = m.version if hasattr(m, "version") else "v1"

    return patch


@pytest.fixture(scope="function")
def setup_test_env(request):
    def teardown():
        Lokii.clean_env(force=True)

    Lokii.setup_env()
    request.addfinalizer(teardown)
