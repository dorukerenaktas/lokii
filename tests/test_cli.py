import os
import shutil
import pytest
from io import StringIO

from config import CONFIG
from lokii import Lokii
from lokii.cli import exec_cmd, LOKII_ASCII


def test_exec_cmd_should_print_help(mocker):
    mock = mocker.patch("sys.stdout", new=StringIO())
    with pytest.raises(SystemExit):
        exec_cmd("lokii -f tests -h")
    assert LOKII_ASCII in mock.getvalue()
    Lokii.clean_env(force=True)


def test_exec_cmd_should_create_log_file():
    log_file_path = "test.log"
    exec_cmd("lokii -f tests -l %s" % log_file_path)
    assert os.path.exists(log_file_path)
    os.remove(log_file_path)


def test_exec_cmd_should_obey_log_level(caplog):
    exec_cmd("lokii -f tests -q")
    assert len(caplog.text) == 0
    exec_cmd("lokii -f tests -v")
    assert len(caplog.text) > 0


@pytest.mark.parametrize(
    "glob_files, load_modules",
    [(["t1.node.py"], [{"source": "INVALID SQL", "item": lambda x: x}])],
    indirect=True,
)
def test_exec_cmd_should_log_errors_with_critical_level(
    glob_files, load_modules, caplog
):
    exec_cmd("lokii -f tests")
    assert "CRITICAL" in caplog.text


@pytest.mark.parametrize("glob_files, load_modules", [([], [])], indirect=True)
def test_exec_cmd_should_clear_db_if_purge(glob_files, load_modules):
    exec_cmd("lokii -f tests -p")
    assert not os.path.exists(CONFIG.temp.db_path)


@pytest.mark.parametrize(
    "glob_files, load_modules",
    [(["t1.node.py"], [{"source": "SELECT 1", "item": lambda x: x}])],
    indirect=True,
)
def test_exec_cmd_should_cache_consequent_runs(glob_files, load_modules, caplog):
    exec_cmd("lokii -f tests")
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()

    exec_cmd("lokii -p -f tests")
    assert "not changed. Using existing dataset." in caplog.text


gen_mod = {"source": "SELECT 1", "item": lambda x: x, "version": "v1"}


@pytest.mark.usefixtures("glob_files", "load_modules")
@pytest.mark.parametrize(
    "glob_files, load_modules", [(["t1.node.py"], [gen_mod])], indirect=True
)
def test_exec_cmd_should_regenerate_on_code_change(caplog):
    # start generation for code version v1
    gen_mod["version"] = "v1"
    exec_cmd("lokii -f tests")
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()

    # start generation for code version v2
    gen_mod["version"] = "v2"
    exec_cmd("lokii -f tests -p")
    # should regenerate and not use cache
    assert "not changed. Using existing dataset." not in caplog.text


gen_mod1, gen_mod2 = (
    {"source": "SELECT * from n2", "item": lambda x: x, "name": "n1"},
    {"source": "SELECT 1", "item": lambda x: x, "name": "n2", "version": "v1"},
)


@pytest.mark.usefixtures("glob_files", "load_modules")
@pytest.mark.parametrize(
    "glob_files, load_modules",
    [(["t1.node.py", "t2.node.py"], [gen_mod1, gen_mod2])],
    indirect=True,
)
def test_exec_cmd_should_regenerate_on_dependency_change(caplog):
    # start generation for dependency code version v1
    gen_mod2["version"] = "v1"
    exec_cmd("lokii  -f tests")
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()

    # start generation for dependency code version v2
    gen_mod2["version"] = "v2"
    exec_cmd("lokii -f tests -p")
    # should regenerate and not use cache because of dependency change
    assert "not changed. Using existing dataset." not in caplog.text
