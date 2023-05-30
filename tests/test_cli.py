import shutil

import pytest
import os.path
from io import StringIO

from config import CONFIG
from lokii import Lokii
from lokii.cli import exec_cmd, LOKII_ASCII


def test_exec_cmd_should_print_help(mocker):
    mock = mocker.patch("sys.stdout", new=StringIO())
    with pytest.raises(SystemExit):
        exec_cmd("lokii -h")
    assert LOKII_ASCII in mock.getvalue()
    Lokii.clean_env(force=True)


def test_exec_cmd_should_create_log_file():
    log_file_path = "test.log"
    exec_cmd("lokii -l %s" % log_file_path)
    assert os.path.exists(log_file_path)
    os.remove(log_file_path)


def test_exec_cmd_should_obey_log_level(caplog):
    exec_cmd("lokii -q")
    assert len(caplog.text) == 0
    exec_cmd("lokii -v")
    assert len(caplog.text) > 0


@pytest.mark.parametrize(
    "m_paths, m_nodes", [(["t1"], [{"source": "INVALID"}])], indirect=True
)
def test_exec_cmd_should_log_errors_with_critical_level(m_paths, m_nodes, caplog):
    exec_cmd("lokii -f .")
    assert "CRITICAL" in caplog.text


@pytest.mark.parametrize("m_paths, m_nodes", [([], [])], indirect=True)
def test_exec_cmd_should_clear_db_if_purge(m_paths, m_nodes):
    exec_cmd("lokii -p")
    assert not os.path.exists(CONFIG.temp.db_path)
    assert os.path.exists("data")
    shutil.rmtree("data")


@pytest.mark.parametrize(
    "m_paths, m_nodes, out_path",
    [(["t1.gen.py"], [{"source": "SELECT 1", "item": lambda x: x}], "test_out_1")],
    indirect=["m_paths", "m_nodes"],
)
def test_exec_cmd_should_execute_generation(m_paths, m_nodes, out_path):
    exec_cmd("lokii -p -o %s -f ." % out_path)
    assert os.path.exists(out_path)
    shutil.rmtree(out_path)


@pytest.mark.parametrize(
    "m_paths, m_nodes, out_path",
    [(["t1.gen.py"], [{"source": "SELECT 1", "item": lambda x: x}], "test_out_1")],
    indirect=["m_paths", "m_nodes"],
)
def test_exec_cmd_should_cache_consequent_runs(m_paths, m_nodes, out_path, caplog):
    exec_cmd("lokii -o %s -f ." % out_path)
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()

    exec_cmd("lokii -p -o %s -f ." % out_path)
    assert "not changed. Using existing dataset." in caplog.text
    assert os.path.exists(out_path)
    shutil.rmtree(out_path)


gen_mod = {"source": "SELECT 1", "item": lambda x: x, "version": "v1"}


@pytest.mark.usefixtures("m_paths", "m_nodes")
@pytest.mark.parametrize("out_path", ["test_out_1"])
@pytest.mark.parametrize(
    "m_paths, m_nodes", [(["t1.gen.py"], [gen_mod])], indirect=True
)
def test_exec_cmd_should_regenerate_on_code_change(caplog, out_path):
    # start generation for code version v1
    gen_mod["version"] = "v1"
    exec_cmd("lokii -o %s -f ." % out_path)
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()

    # start generation for code version v2
    gen_mod["version"] = "v2"
    exec_cmd("lokii -p -o %s -f ." % out_path)
    # should regenerate and not use cache
    assert "not changed. Using existing dataset." not in caplog.text
    assert os.path.exists(out_path)
    shutil.rmtree(out_path)


gen_mod1, gen_mod2 = (
    {"source": "SELECT 1", "item": lambda x: x, "wait": ["n2"], "name": "n1"},
    {"source": "SELECT 1", "item": lambda x: x, "name": "n2", "version": "v1"},
)


@pytest.mark.usefixtures("m_paths", "m_nodes")
@pytest.mark.parametrize("out_path", ["test_out_1"])
@pytest.mark.parametrize(
    "m_paths, m_nodes",
    [(["t1.gen.py", "t2.gen.py"], [gen_mod1, gen_mod2])],
    indirect=True,
)
def test_exec_cmd_should_regenerate_on_dependency_change(caplog, out_path):
    # start generation for dependency code version v1
    gen_mod2["version"] = "v1"
    exec_cmd("lokii -o %s -f ." % out_path)
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()

    # start generation for dependency code version v2
    gen_mod2["version"] = "v2"
    exec_cmd("lokii -p -o %s -f ." % out_path)
    # should regenerate and not use cache because of dependency change
    assert "not changed. Using existing dataset." not in caplog.text
    assert os.path.exists(out_path)
    shutil.rmtree(out_path)
