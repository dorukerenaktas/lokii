import os

import pytest
from unittest.mock import Mock

from lokii import Lokii
from parse.node_parser import NODE_RESOLVER


@pytest.fixture
def found_mods(mocker, request):
    gen_files = request.param or []
    gen_files = [m if ".gen.py" in m else f"{m}.gen.py" for m in gen_files]
    mocker.patch(
        "glob.glob",
        lambda p: [os.path.join(p.replace(NODE_RESOLVER, ""), f) for f in gen_files],
    )

    node_names = [os.path.basename(m).replace(".gen.py", "") for m in gen_files]
    return node_names


@pytest.fixture
def loaded_mods(mocker, found_mods, request):
    def module_file_loader_side_effect(file_path: str):
        mods = request.param or []
        mod_i = found_mods.index(os.path.basename(file_path).replace(".gen.py", ""))
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


@pytest.fixture(scope="function")
def setup_test_env(request):
    def teardown():
        Lokii.clean_env(force=True)

    Lokii.setup_env()
    request.addfinalizer(teardown)
