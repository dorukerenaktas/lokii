import os
import pytest

from lokii.model.node_module import GenNodeModule as Gm
from lokii.parse.node_parser import NodeParser

pytestmark = [pytest.mark.usefixtures("m_paths", "m_nodes")]


@pytest.mark.parametrize("m_paths, m_nodes", [([], [])], indirect=True)
def test_parse_should_log_warning_if_no_modules_found(caplog):
    NodeParser("/test/path").parse()
    assert "No generation node file found" in caplog.text


@pytest.mark.parametrize(
    "m_paths, m_nodes",
    [
        (
            ["/test/path/t1.gen.py", "/test/path/g1/t2.gen.py"],
            [
                {"source": "SELECT 1", "item": lambda x: x},
                {"source": "SELECT 1", "item": lambda x: x},
            ],
        )
    ],
    indirect=True,
)
def test_parse_should_use_filename_if_name_not_provided(m_paths):
    parsed = NodeParser("/test/path").parse()
    for module_path in m_paths:
        node_name = module_path.replace(".gen.py", "")
        assert node_name == parsed[node_name].name


@pytest.mark.parametrize(
    "m_paths, m_nodes",
    [
        (
            ["/test/path/t1.gen.py", "/test/path/g1/t2.gen.py"],
            [
                {"source": "SELECT 1", "item": lambda x: x, "name": "test3"},
                {"source": "SELECT 1", "item": lambda x: x, "name": "test4"},
            ],
        )
    ],
    indirect=True,
)
def test_parse_should_use_name_instead_of_filename(m_paths, m_nodes):
    parsed = NodeParser("/test/path").parse()
    for i, module_path in enumerate(m_paths):
        node_name = m_nodes[i]["name"]
        assert node_name == parsed[node_name].name


@pytest.mark.parametrize(
    "m_paths, m_nodes, expect",
    [
        (
            ["/test/path/g1/t1.gen.py", "/test/path/g1/g2/t2.gen.py"],
            [
                {"source": "SELECT 1", "item": lambda x: x, "name": "test3"},
                {"source": "SELECT 1", "item": lambda x: x, "name": "test4"},
            ],
            [["g1"], ["g1", "g2"]],
        )
    ],
    indirect=["m_paths", "m_nodes"],
)
def test_parse_should_use_file_path_to_extract_groups(m_paths, m_nodes, expect):
    parser = NodeParser("/test/path")
    parser.parse()
    for i, module_path in enumerate(m_paths):
        node_name = m_nodes[i]["name"]
        assert expect[i] == parser.nodes[node_name].groups


@pytest.mark.parametrize("m_paths", [["/test/path/g1/t1.gen.py"]], indirect=True)
@pytest.mark.parametrize(
    "m_nodes, expect",
    [
        ([{}], "`source` not found"),
        ([{"source": 1000}], "`source` must be str"),
        ([{"source": "1"}], "`item` not found"),
        ([{"source": "1", "item": ""}], "`item` must be function"),
        ([{"source": "1", "item": lambda x, y: x}], "`item` accepts only one param"),
        ([{"source": "1", "item": lambda x: x, "wait": "n1"}], "`wait` must be list"),
        ([{"source": "1", "item": lambda x: x, "name": 10}], "`name` must be str"),
    ],
    indirect=["m_nodes"],
)
def test_parse_raise_error_if_module_not_valid(expect):
    with pytest.raises(AssertionError) as err:
        NodeParser("/test/path").parse()
    assert expect in str(err.value)
