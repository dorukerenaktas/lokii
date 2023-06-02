import os
import shutil

import pytest
from pytest import FixtureRequest
from pytest_mock import MockerFixture


from lokii.config import CONFIG
from lokii import Lokii


@pytest.fixture
def glob_files(mocker, request):
    """
    :param mocker: Fixture that provides the same interface to functions in the mock module,
    ensuring that they are uninstalled at the end of each test.
    :type mocker: MockerFixture
    :param request: A request for a fixture from a test or fixture function.
    :type request: FixtureRequest
    :return: list of found files
    :rtype: list[str]
    """
    files = request.param if hasattr(request, "param") else []
    files = [os.path.normpath(f) for f in files]
    mocker.patch(
        "lokii.parse.group_parser.glob",
        return_value=[f for f in files if CONFIG.gen.group_ext in f],
    )
    mocker.patch(
        "lokii.parse.node_parser.glob",
        return_value=[f for f in files if CONFIG.gen.node_ext in f],
    )
    return files


@pytest.fixture
def load_modules(mocker, request, glob_files):
    """
    :param mocker: Fixture that provides the same interface to functions in the mock module,
    ensuring that they are uninstalled at the end of each test.
    :type mocker: MockerFixture
    :param request: A request for a fixture from a test or fixture function.
    :type request: FixtureRequest
    :param glob_files: A glob mock fixture from a test or fixture function.
    :type glob_files: list[str]
    """

    def module_file_loader_side_effect(file_path: str):
        mods = request.param if hasattr(request, "param") else []
        mod_i = glob_files.index(file_path)
        loader = {
            "load": mocker.Mock(),
            "module": type("object", (object,), mods[mod_i]),
            "version": mods[mod_i]["version"] if "version" in mods[mod_i] else "v1",
        }
        return type("ModuleFileLoader", (object,), loader or {})()

    group_mock = mocker.patch("lokii.parse.group_parser.ModuleFileLoader")
    group_mock.side_effect = module_file_loader_side_effect

    node_mock = mocker.patch("lokii.parse.node_parser.ModuleFileLoader")
    node_mock.side_effect = module_file_loader_side_effect
    return request.param if hasattr(request, "param") else []


@pytest.fixture(scope="function")
def setup_test_env(request):
    def teardown():
        Lokii.clean_env(force=True)
        if os.path.exists("data"):
            shutil.rmtree("data")

    Lokii.setup_env()
    request.addfinalizer(teardown)
