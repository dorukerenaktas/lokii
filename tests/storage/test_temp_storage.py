from lokii.storage.temp_storage import TempStorage


def test_dump_should_save_to_temp_file_path_dir(mocker):
    mocker.patch("builtins.open")
    mocker.patch("os.path.exists")
    mock = mocker.patch("json.dumps")

    data = [{"data": "test1"}, {"data": "test2"}]
    TempStorage("test").dump(data)
    assert mock.call_count
    assert data in mock.call_args.args
