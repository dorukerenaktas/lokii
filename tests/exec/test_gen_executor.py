import pytest
import os

from lokii.exec.gen_executor import GenExecutor
from lokii.storage.data_storage import DataStorage
from tests.conftest import mock_gen_run as mgr


@pytest.mark.usefixtures("setup_test_env")
def test_prepare_node_should_return_total_target_count_for_query():
    data_storage = DataStorage()
    executor = GenExecutor(mgr(s="SELECT * FROM range(100)"), data_storage)
    assert executor.prepare_node() == 100


@pytest.mark.usefixtures("setup_test_env")
def test_exec_node_should_return_generated_list_of_files():
    data_storage = DataStorage()
    executor = GenExecutor(mgr(n="test", s="SELECT * FROM range(100)"), data_storage)
    executor.prepare_node()
    files = executor.exec_node()
    assert len(files) == 1
    assert os.path.exists(files[0])
