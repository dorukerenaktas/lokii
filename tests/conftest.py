from typing import Callable

import pytest

from lokii import Lokii
from model.gen_module import GenRun


def gen_func(args) -> dict:
    return args


def mock_gen_conf(s="", w: list[str] = None, f: Callable = None):
    func: Callable[[dict], dict] = f or gen_func
    return {"source": s, "wait": w or [], "func": func}


def mock_gen_run(n="", v="", i=0, s="", w: list[str] = None, f: Callable = None):
    return GenRun(n, v, i, mock_gen_conf(s, w, f))


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
