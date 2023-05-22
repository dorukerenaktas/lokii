import pytest
from unittest import mock

from model.gen_module import GenRun
from parse.gen_node_parser import GenNodeParser


@pytest.fixture
def mock_module(mocker, node_conf):
    mocker.patch("parse.gen_node_parser.glob.glob", return_value=["test.gen.py"])

    module = type("obj", (object,), {"runs": node_conf})
    mocker.patch(
        "lokii.util.module_file_loader.ModuleFileLoader.load", return_value=module
    )


@mock.patch("parse.gen_node_parser.glob.glob", lambda *args: [])
def test_parse_log_warning_if_no_modules_found(caplog):
    parser = GenNodeParser("/test/path")
    parser.parse()
    assert "No generation node file found" in caplog.text


@pytest.mark.usefixtures("mock_module")
@pytest.mark.parametrize(
    "node_conf, expect",
    [
        (None, "`runs` configuration not found"),
        ("config", "`runs` must be list"),
        ([], "`runs` has no items"),
        ([{"source": []}], "[`source`] must be str"),
        ([{"source": "", "wait": ""}], "[`wait`] must be list"),
        ([{"source": "", "rels": ""}], "[`rels`] must be dict"),
        ([{"source": ""}], "[`func`] not found"),
        ([{"source": "", "func": ""}], "[`func`] must be function"),
        ([{"source": "", "func": lambda x, y: x}], "[`func`] must accept only one"),
    ],
)
def test_parse_raise_error_if_module_not_valid(expect):
    parser = GenNodeParser("/test/path")
    with pytest.raises(AssertionError) as err:
        parser.parse()
    assert expect in str(err.value)


def gen_test_func(_):
    pass


@pytest.mark.usefixtures("mock_module")
@pytest.mark.parametrize(
    "node_conf, expect",
    [
        (
            [{"source": "q", "func": lambda x: x}],
            GenRun(
                "test",
                0,
                {"source": "q", "wait": [], "rels": {}, "func": lambda x: x},
            ),
        ),
    ],
)
def test_parse_should_return_module_if_valid(expect):
    parser = GenNodeParser("/test/path")
    parsed = parser.parse()
    assert len(parsed) == 1
    assert parsed["test/0"].run_key == expect.run_key
    assert parsed["test/0"].source == expect.source
    assert parsed["test/0"].wait == expect.wait
    assert parsed["test/0"].rels == expect.rels


def test_analyze_should_raise_error_if_cyclic_dependencies_exists():
    parser = GenNodeParser("/test/path")
    parser.gen_runs = {
        "n1": type("obj", (object,), {"run_key": "n1", "wait": ["n3"]}),
        "n2": type("obj", (object,), {"run_key": "n2", "wait": ["n1", "n3"]}),
        "n3": type("obj", (object,), {"run_key": "n3", "wait": ["n2"]}),
    }
    with pytest.raises(AssertionError) as err:
        parser.order()
    assert "Found cyclic dependencies" in str(err.value)


def test_analyze_should_return_execution_order():
    parser = GenNodeParser("/test/path")
    parser.gen_runs = {
        "n1": type("obj", (object,), {"run_key": "n1", "wait": ["n3"]}),
        "n2": type("obj", (object,), {"run_key": "n2", "wait": ["n1", "n3"]}),
        "n3": type("obj", (object,), {"run_key": "n3", "wait": []}),
    }
    order = parser.order()
    assert order == ["n3", "n1", "n2"]
