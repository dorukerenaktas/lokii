import os.path

import pytest

from lokii.config import CONFIG
from lokii.storage.data_storage import DataStorage
from lokii.storage.temp_storage import TempStorage


@pytest.mark.usefixtures("setup_test_env")
def test_init_should_create_database_and_meta_table():
    storage = DataStorage()
    assert os.path.exists(CONFIG.temp.db_path)
    assert "__meta" in storage._conn.execute("SHOW TABLES;").fetchone()


@pytest.mark.usefixtures("setup_test_env")
def test_count_should_return_row_count_for_query_result():
    storage = DataStorage()
    assert storage.count("SELECT unnest([1, 2, 3])") == 3


@pytest.mark.usefixtures("setup_test_env")
def test_exec_should_return_query_result_for_given_page():
    storage = DataStorage()
    q = "SELECT * FROM range(0, 25)"
    first_page = storage.exec(q, 0, 20)
    second_page = storage.exec(q, 1, 20)
    assert len(first_page) == 20
    assert first_page[0]["range"] == 0
    assert len(second_page) == 5
    assert second_page[0]["range"] == 20


@pytest.mark.usefixtures("setup_test_env")
def test_save_should_insert_record_to_meta_table():
    storage = DataStorage()
    storage.save("test_gen1", "test_key1", "test_v1")
    records = storage._conn.execute("SELECT * FROM main.__meta").fetchall()
    assert len([r for r in records if "test_key1" in r]) == 1


@pytest.mark.usefixtures("setup_test_env")
def test_save_should_replace_record_with_same_key():
    storage = DataStorage()
    storage.save("test_gen1", "test_key1", "test_v1")
    storage.save("test_gen2", "test_key1", "test_v4")
    records = storage._conn.execute("SELECT * FROM main.__meta").fetchall()
    assert len([r for r in records if "test_key1" in r]) == 1


@pytest.mark.usefixtures("setup_test_env")
def test_meta_should_return_data_for_given_keys():
    storage = DataStorage()
    storage.save("test_gen1", "test_key1", "test_v1")
    storage.save("test_gen1", "test_key2", "test_v1")
    storage.save("test_gen2", "test_key3", "test_v4")
    deps = storage.meta(["test_key2", "test_key3"])
    assert len(deps) == 2
    assert len([d for d in deps if d["run_key"] == "test_key2"]) == 1
    assert len([d for d in deps if d["run_key"] == "test_key3"]) == 1


@pytest.mark.usefixtures("setup_test_env")
@pytest.mark.parametrize("node, expect", [("s1.n2", "s1"), ("s2.n2", "s2")])
def test_insert_should_create_schema_if_node_name_contain_dot(node, expect):
    _temp = TempStorage(node)
    _temp.dump([{"data": i} for i in range(10)])
    storage = DataStorage()
    storage.insert(node, _temp.batches)
    res = storage._conn.execute(
        f"SELECT * FROM information_schema.schemata WHERE schema_name = '{expect}';"
    ).fetchone()
    assert expect in res


@pytest.mark.usefixtures("setup_test_env")
@pytest.mark.parametrize("loop, expect", [([7], 7), ([12, 10, 7], 29)])
def test_insert_should_create_table_from_generated_files(loop, expect):
    _temp = TempStorage("n1")
    for count in loop:
        _temp.dump([{"data": i} for i in range(count)])
    storage = DataStorage()
    storage.insert("n1", _temp.batches)
    assert expect in storage._conn.execute(f"SELECT COUNT() FROM n1;").fetchone()
