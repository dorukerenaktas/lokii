import os
import shutil

import pytest
from pytest import FixtureRequest
from pytest_mock import MockerFixture

from lokii import Lokii


@pytest.fixture
def m_paths(mocker, request):
    gen_files = request.param or []
    mocker.patch("glob.glob", return_value=gen_files)

    node_names = [os.path.basename(m).replace(".gen.py", "") for m in gen_files]
    return node_names


@pytest.fixture
def m_nodes(mocker, request, m_paths):
    """

    :param mocker: Fixture that provides the same interface to functions in the mock module,
    ensuring that they are uninstalled at the end of each test.
    :type mocker: MockerFixture
    :param request: A request for a fixture from a test or fixture function.
    :type request: FixtureRequest
    """
    mods = request.param if hasattr(request, "param") else []

    def module_file_loader_side_effect(file_path: str):
        mod_i = m_paths.index(os.path.basename(file_path).replace(".gen.py", ""))
        loader = {
            "load": mocker.Mock(),
            "module": type("obj", (object,), mods[mod_i]),
            "version": mods[mod_i]["version"] if "version" in mods[mod_i] else "v1",
        }
        return type("ModuleFileLoader", (object,), loader or {})()

    mock = mocker.patch("lokii.parse.node_parser.ModuleFileLoader")
    mock.side_effect = module_file_loader_side_effect
    return mods


@pytest.fixture(scope="function")
def setup_test_env(request):
    def teardown():
        Lokii.clean_env(force=True)
        if os.path.exists("data"):
            shutil.rmtree("data")

    Lokii.setup_env()
    request.addfinalizer(teardown)
