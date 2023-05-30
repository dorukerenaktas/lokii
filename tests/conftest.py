import os
import pytest
from unittest.mock import Mock

from lokii import Lokii


@pytest.fixture
def m_paths(mocker, request):
    gen_files = request.param or []
    mocker.patch("glob.glob", return_value=gen_files)

    node_names = [os.path.basename(m).replace(".gen.py", "") for m in gen_files]
    return node_names


@pytest.fixture
def m_nodes(mocker, m_paths, request):
    def module_file_loader_side_effect(file_path: str):
        mods = request.param or []
        mod_i = m_paths.index(os.path.basename(file_path).replace(".gen.py", ""))
        loader = {
            "load": Mock(),
            "module": type("obj", (object,), mods[mod_i]),
            "version": mods[mod_i]["version"] if "version" in mods[mod_i] else "v1",
        }
        return type("ModuleFileLoader", (object,), loader or {})()

    mock = mocker.patch("lokii.parse.node_parser.ModuleFileLoader")
    mock.side_effect = module_file_loader_side_effect
    return request.param or []


@pytest.fixture(scope="function")
def setup_test_env(request):
    def teardown():
        Lokii.clean_env(force=True)

    Lokii.setup_env()
    request.addfinalizer(teardown)
