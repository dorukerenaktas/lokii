import pytest

from lokii.parse.group_parser import GroupParser

pytestmark = [pytest.mark.usefixtures("glob_files", "load_modules")]


@pytest.mark.parametrize("glob_files, load_modules", [([], [])], indirect=True)
def test_parse_should_log_warning_if_no_modules_found(glob_files, load_modules, caplog):
    GroupParser("/test/proj").parse()
    assert "No group conf file found" in caplog.text


@pytest.mark.parametrize("load_modules", [[{}]], indirect=True)
@pytest.mark.parametrize(
    "glob_files, expect",
    [(["/test/proj/test.group.py"], "proj"), (["/test/proj/g1/test.group.py"], "g1")],
    indirect=["glob_files"],
)
def test_parse_should_use_folder_name_as_group_identifier(
    glob_files, load_modules, expect
):
    parsed = GroupParser("/test/proj").parse()
    assert expect in parsed
    assert expect == parsed[expect].name


@pytest.mark.parametrize(
    "glob_files, load_modules, expect",
    [
        (
            ["/test/path/g1/t1.group.py", "/test/path/g1/g2/t2.group.py"],
            [{"name": "g1"}, {"name": "g2"}],
            [[], ["g1"]],
        )
    ],
    indirect=["glob_files", "load_modules"],
)
def test_parse_should_use_file_path_to_extract_groups(glob_files, load_modules, expect):
    parser = GroupParser("/test/path")
    parser.parse()
    for i, module_path in enumerate(glob_files):
        node_name = load_modules[i]["name"]
        assert expect[i] == parser.groups[node_name].groups


@pytest.mark.parametrize("glob_files", [["/test/path/g1/g1.group.py"]], indirect=True)
@pytest.mark.parametrize(
    "load_modules, expect",
    [
        ([{"before": ""}], "`before` must be function"),
        ([{"before": lambda x, y: x}], "`before` accepts only one param"),
        ([{"export": ""}], "`export` must be function"),
        ([{"export": lambda x, y: x}], "`export` accepts only one param"),
        ([{"after": ""}], "`after` must be function"),
        ([{"after": lambda x, y: x}], "`after` accepts only one param"),
    ],
    indirect=["load_modules"],
)
def test_parse_raise_error_if_module_not_valid(glob_files, load_modules, expect):
    with pytest.raises(AssertionError) as err:
        GroupParser("/test/proj").parse()
    assert expect in str(err.value)
