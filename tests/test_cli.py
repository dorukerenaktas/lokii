import shutil

import pytest
import os.path
from io import StringIO

from config import CONFIG
from lokii import Lokii
from lokii.cli import execute_command_line, LOKII_ASCII
from tests.conftest import mock_gen_conf as mgc


def test_execute_command_line_should_print_help(mocker):
    mock: StringIO = mocker.patch("sys.stdout", new=StringIO())
    with pytest.raises(SystemExit):
        execute_command_line("lokii -h")
    assert LOKII_ASCII in mock.getvalue()
    Lokii.clean_env(force=True)


def test_execute_command_line_should_create_log_file():
    log_file_path = "test.log"
    execute_command_line(f"lokii -l {log_file_path}")
    assert os.path.exists(log_file_path)
    os.remove(log_file_path)


def test_execute_command_line_should_obey_log_level(caplog):
    execute_command_line(f"lokii -q")
    assert len(caplog.text) == 0
    execute_command_line(f"lokii -v")
    assert len(caplog.text) > 0


def test_execute_command_line_should_clear_db_if_purge(mock_module_loader):
    execute_command_line(f"lokii -p")
    assert not os.path.exists(CONFIG.temp.db_path)
    assert os.path.exists("data")
    shutil.rmtree("data")


def test_execute_command_line_should_execute_generation(mock_module_loader):
    mock_module_loader(["test.gen.py"], {"runs": [mgc(s="SELECT * FROM range(100)")]})
    execute_command_line(f"lokii -p -o data -f .")
    assert os.path.exists("data")
    shutil.rmtree("data")


def test_execute_command_line_should_cache_consequent_runs(caplog, mock_module_loader):
    mock_module_loader(["test.gen.py"], {"runs": [mgc(s="SELECT * FROM range(100)")]})
    execute_command_line(f"lokii -o data -f .")
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()
    execute_command_line(f"lokii -p -o data -f .")
    assert "not changed. Using existing dataset." in caplog.text
    assert os.path.exists("data")
    shutil.rmtree("data")


def test_execute_command_line_should_regenerate_on_code_change(
    caplog, mock_module_loader
):
    conf = {"version": "v1", "runs": [mgc(s="SELECT * FROM range(100)")]}
    mock_module_loader(["test.gen.py"], conf)
    # start generation for code version v1
    execute_command_line(f"lokii -o data -f .")
    assert os.path.exists(CONFIG.temp.db_path)
    caplog.clear()

    # start generation for code version v2
    mock_module_loader(["test.gen.py"], {**conf, "version": "v2"})
    execute_command_line(f"lokii -p -o data -f .")
    # should regenerate and not use cache
    assert "not changed. Using existing dataset." not in caplog.text
    assert os.path.exists("data")
    shutil.rmtree("data")
