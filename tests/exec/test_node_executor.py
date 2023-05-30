from unittest.mock import Mock

import pytest
import os

from lokii.storage.data_storage import DataStorage
from lokii.exec.node_executor import NodeExecutor, _exec_chunk
from lokii.model.node_module import GenNodeModule


@pytest.mark.usefixtures("setup_test_env")
def test__exec_chunk_should_call_func_for_list_length():
    func = Mock()
    _exec_chunk(func, [{"data": f} for f in range(100)])
    assert func.call_count == 100


@pytest.mark.usefixtures("setup_test_env")
def test_prepare_node_should_return_total_target_count_for_query():
    data_storage = DataStorage()
    node = GenNodeModule("SELECT 1", lambda x: x, name="n1")
    executor = NodeExecutor(node, data_storage)
    assert executor.prepare_node() == 1


@pytest.mark.usefixtures("setup_test_env")
def test_exec_node_should_return_generated_list_of_files():
    data_storage = DataStorage()
    node = GenNodeModule("SELECT 1", lambda x: x, name="n1")
    executor = NodeExecutor(node, data_storage)
    executor.prepare_node()
    files = executor.exec_node()
    assert len(files) == 1
    assert os.path.exists(files[0])
