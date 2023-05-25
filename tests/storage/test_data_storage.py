import os.path

from config import CONFIG
from storage.data_storage import DataStorage
from storage.temp_storage import TempStorage


def test_init_should_create_database_and_meta_table():
    storage = DataStorage()
    assert os.path.exists(CONFIG.temp.db_path)
    assert "__meta" in storage._conn.execute("SHOW TABLES;").fetchone()


def test_count_should_return_row_count_for_query_result():
    storage = DataStorage()
    assert storage.count("SELECT unnest([1, 2, 3])") == 3


def test_exec_should_return_query_result_for_given_page():
    storage = DataStorage()
    q = "SELECT * FROM range(0, 25)"
    first_page = storage.exec(q, 0, 20)
    second_page = storage.exec(q, 1, 20)
    assert len(first_page) == 20
    assert first_page[0]["range"] == 0
    assert len(second_page) == 5
    assert second_page[0]["range"] == 20


def test_save_should_insert_record_to_meta_table():
    storage = DataStorage()
    storage.save("test_gen1", "test_key1", "test_v1")
    records = storage._conn.execute("SELECT * FROM main.__meta").fetchall()
    assert len([r for r in records if "test_key1" in r]) == 1


def test_save_should_replace_record_with_same_key():
    storage = DataStorage()
    storage.save("test_gen1", "test_key1", "test_v1")
    storage.save("test_gen2", "test_key1", "test_v4")
    records = storage._conn.execute("SELECT * FROM main.__meta").fetchall()
    assert len([r for r in records if "test_key1" in r]) == 1


def test_meta_should_return_data_for_given_keys():
    storage = DataStorage()
    storage.save("test_gen1", "test_key1", "test_v1")
    storage.save("test_gen1", "test_key2", "test_v1")
    storage.save("test_gen2", "test_key3", "test_v4")
    deps = storage.meta(["test_key2", "test_key3"])
    assert len(deps) == 2
    assert len([d for d in deps if d["run_key"] == "test_key2"]) == 1
    assert len([d for d in deps if d["run_key"] == "test_key3"]) == 1


def test_insert_should_create_schema_if_node_name_contain_dot():
    _temp = TempStorage("schema1.node1")
    _temp.dump([{"data": i} for i in range(10)])
    storage = DataStorage()
    storage.insert("schema1.node1", _temp.batches)
    res = storage._conn.execute(
        f"SELECT * FROM information_schema.schemata WHERE schema_name = '{'schema1'}';"
    ).fetchone()
    assert "schema1" in res


def test_insert_should_create_table_from_generated_files():
    _temp = TempStorage("schema1.node1")
    _temp.dump([{"data": i} for i in range(10)])
    _temp.dump([{"data": i} for i in range(10)])
    storage = DataStorage()
    storage.insert("schema1.node1", _temp.batches)
    assert 20 in storage._conn.execute(f"SELECT COUNT() FROM schema1.node1;").fetchone()
