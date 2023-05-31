import os
import pytest
from lokii.config import CONFIG

from lokii.parse.node_parser import NodeParser

pytestmark = [pytest.mark.usefixtures("glob_files", "load_modules")]


@pytest.mark.parametrize("glob_files, load_modules", [([], [])], indirect=True)
def test_parse_should_log_warning_if_no_modules_found(caplog):
    NodeParser("/test/path").parse()
    assert "No generation node file found" in caplog.text


@pytest.mark.parametrize(
    "glob_files, load_modules",
    [
        (
            ["/test/path/t1.node.py", "/test/path/g1/t2.node.py"],
            [
                {"source": "SELECT 1", "item": lambda x: x},
                {"source": "SELECT 1", "item": lambda x: x},
            ],
        )
    ],
    indirect=True,
)
def test_parse_should_use_filename_if_name_not_provided(glob_files, load_modules):
    parsed = NodeParser("/test/path").parse()
    for module_path in glob_files:
        node_name = os.path.basename(module_path).replace(CONFIG.gen.node_ext, "")
        assert node_name == parsed[node_name].name


@pytest.mark.parametrize(
    "glob_files, load_modules",
    [
        (
            ["/test/path/t1.node.py", "/test/path/g1/t2.node.py"],
            [
                {"source": "SELECT 1", "item": lambda x: x, "name": "test3"},
                {"source": "SELECT 1", "item": lambda x: x, "name": "test4"},
            ],
        )
    ],
    indirect=True,
)
def test_parse_should_use_name_instead_of_filename(glob_files, load_modules):
    parsed = NodeParser("/test/path").parse()
    for i, module_path in enumerate(glob_files):
        node_name = load_modules[i]["name"]
        assert node_name == parsed[node_name].name


@pytest.mark.parametrize(
    "glob_files, load_modules, expect",
    [
        (
            ["/test/path/g1/t1.node.py", "/test/path/g1/g2/t2.node.py"],
            [
                {"source": "SELECT 1", "item": lambda x: x, "name": "test3"},
                {"source": "SELECT 1", "item": lambda x: x, "name": "test4"},
            ],
            [["g1"], ["g1", "g2"]],
        )
    ],
    indirect=["glob_files", "load_modules"],
)
def test_parse_should_use_file_path_to_extract_groups(glob_files, load_modules, expect):
    parser = NodeParser("/test/path")
    parser.parse()
    for i, module_path in enumerate(glob_files):
        node_name = load_modules[i]["name"]
        assert expect[i] == parser.nodes[node_name].groups


@pytest.mark.parametrize("glob_files", [["/test/path/g1/t1.node.py"]], indirect=True)
@pytest.mark.parametrize(
    "load_modules, expect",
    [
        ([{}], "`source` not found"),
        ([{"source": 1000}], "`source` must be str"),
        ([{"source": "1"}], "`item` not found"),
        ([{"source": "1", "item": ""}], "`item` must be function"),
        ([{"source": "1", "item": lambda x, y: x}], "`item` accepts only one param"),
        ([{"source": "1", "item": lambda x: x, "name": 10}], "`name` must be str"),
    ],
    indirect=["load_modules"],
)
def test_parse_raise_error_if_module_not_valid(expect):
    with pytest.raises(AssertionError) as err:
        NodeParser("/test/path").parse()
    assert expect in str(err.value)
