import shutil

import pytest
import os.path
from io import StringIO

from config import CONFIG
from lokii import Lokii
from lokii.cli import exec_cmd, LOKII_ASCII
from lokii.model.gen_module import GenNodeModule as Gm


def test_exec_cmd_should_print_help(mocker):
    mock: StringIO = mocker.patch("sys.stdout", new=StringIO())
    with pytest.raises(SystemExit):
        exec_cmd("lokii -h")
    assert LOKII_ASCII in mock.getvalue()
    Lokii.clean_env(force=True)


def test_exec_cmd_should_create_log_file():
    log_file_path = "test.log"
    exec_cmd(f"lokii -l {log_file_path}")
    assert os.path.exists(log_file_path)
    os.remove(log_file_path)


def test_exec_cmd_should_obey_log_level(caplog):
    exec_cmd("lokii -q")
    assert len(caplog.text) == 0
    exec_cmd("lokii -v")
    assert len(caplog.text) > 0


# noinspection SpellCheckingInspection, PyTestParametrized, PyTypeChecker
@pytest.mark.usefixtures("found_mods", "loaded_mods")
@pytest.mark.parametrize(
    "found_mods, loaded_mods",
    [(["t1"], [Gm([{"source": "INVALID SQL"}])])],
    indirect=True,
)
def test_exec_cmd_should_log_errors_with_critical_level(caplog):
    exec_cmd("lokii -f .")
    assert "CRITICAL" in caplog.text


# noinspection SpellCheckingInspection, PyTestParametrized, PyTypeChecker
@pytest.mark.usefixtures("found_mods", "loaded_mods")
@pytest.mark.parametrize("found_mods, loaded_mods", [([], [])], indirect=True)
def test_exec_cmd_should_clear_db_if_purge():
    exec_cmd("lokii -p")
    assert not os.path.exists(CONFIG.temp.db_path)
    assert os.path.exists("data")
    shutil.rmtree("data")


# noinspection SpellCheckingInspection, PyTestParametrized, PyTypeChecker
@pytest.mark.usefixtures("found_mods", "loaded_mods")
@pytest.mark.parametrize("outpath", ["test_out_1"])
@pytest.mark.parametrize(
    "found_mods, loaded_mods",
    [(["t1.gen.py"], [Gm([{"source": "SELECT * FROM range(100)"}])])],
    indirect=True,
)
def test_exec_cmd_should_execute_generation(outpath):
    exec_cmd(f"lokii -p -o {outpath} -f .")
    assert os.path.exists(outpath)
    shutil.rmtree(outpath)


# noinspection SpellCheckingInspection, PyTestParametrized, PyTypeChecker
@pytest.mark.usefixtures("found_mods", "loaded_mods")
@pytest.mark.parametrize("outpath", ["test_out_1"])
@pytest.mark.parametrize(
    "found_mods, loaded_mods",
    [(["t1.gen.py"], [Gm([{"source": "SELECT * FROM range(100)"}])])],
    indirect=True,
)
def test_exec_cmd_should_cache_consequent_runs(caplog, outpath):
    exec_cmd(f"lokii -o {outpath} -f .")
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()

    # start generation for second time without any code or dependency change
    exec_cmd(f"lokii -p -o {outpath} -f .")
    assert "not changed. Using existing dataset." in caplog.text
    assert os.path.exists(outpath)
    shutil.rmtree(outpath)


# noinspection PyTypeChecker
gen_mod = Gm([{"source": "SELECT * FROM range(100)"}], version="v1")


# noinspection SpellCheckingInspection, PyTestParametrized
@pytest.mark.usefixtures("found_mods", "loaded_mods")
@pytest.mark.parametrize("outpath", ["test_out_1"])
@pytest.mark.parametrize(
    "found_mods, loaded_mods", [(["t1.gen.py"], [gen_mod])], indirect=True
)
def test_exec_cmd_should_regenerate_on_code_change(caplog, outpath):
    # start generation for code version v1
    gen_mod.version = "v1"
    exec_cmd(f"lokii -o {outpath} -f .")
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()

    # start generation for code version v2
    gen_mod.version = "v2"
    exec_cmd("lokii -p -o data -f .")
    # should regenerate and not use cache
    assert "not changed. Using existing dataset." not in caplog.text
    assert os.path.exists(outpath)
    shutil.rmtree(outpath)


# noinspection PyTypeChecker
gen_mod1, gen_mod2 = (
    Gm([{"source": "SELECT * FROM range(100)", "wait": ["n2"]}], name="n1"),
    Gm([{"source": "SELECT * FROM range(100)"}], name="n2", version="v1"),
)


# noinspection SpellCheckingInspection, PyTestParametrized
@pytest.mark.usefixtures("found_mods", "loaded_mods")
@pytest.mark.parametrize("outpath", ["test_out_1"])
@pytest.mark.parametrize(
    "found_mods, loaded_mods",
    [(["t1.gen.py", "t2.gen.py"], [gen_mod1, gen_mod2])],
    indirect=True,
)
def test_exec_cmd_should_regenerate_on_dependency_change(caplog, outpath):
    # start generation for dependency code version v1
    gen_mod2.version = "v1"
    exec_cmd(f"lokii -o {outpath} -f .")
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()

    # start generation for dependency code version v2
    gen_mod2.version = "v2"
    exec_cmd("lokii -p -o data -f .")
    # should regenerate and not use cache because of dependency change
    assert "not changed. Using existing dataset." not in caplog.text
    assert os.path.exists(outpath)
    shutil.rmtree(outpath)
