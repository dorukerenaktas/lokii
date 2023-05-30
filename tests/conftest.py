import os
import shutil

import pytest
from pytest import FixtureRequest
from pytest_mock import MockerFixture

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
    mocker.patch("lokii.parse.node_parser.glob", return_value=files)
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
            "module": type("GenNodeModule", (object,), mods[mod_i]),
            "version": mods[mod_i]["version"] if "version" in mods[mod_i] else "v1",
        }
        return type("ModuleFileLoader", (object,), loader or {})()

    mock = mocker.patch("lokii.parse.node_parser.ModuleFileLoader")
    mock.side_effect = module_file_loader_side_effect
    return request.param if hasattr(request, "param") else []


@pytest.fixture(scope="function")
def setup_test_env(request):
    def teardown():
        Lokii.clean_env(force=True)
        if os.path.exists("data"):
            shutil.rmtree("data")

    Lokii.setup_env()
    request.addfinalizer(teardown)
