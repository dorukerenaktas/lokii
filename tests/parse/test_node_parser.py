import pytest

from model.gen_module import GenRun, GenRunConf
from parse.node_parser import NodeParser

conf: GenRunConf = {"source": "test", "wait": [], "rels": {}, "func": lambda x: x}


@pytest.fixture
def mock_loader(mocker):
    def patch(files: list[str] = None, node: dict = None) -> None:
        mocker.patch("glob.glob", return_value=files or [])
        mocker.patch("inspect.getsource", return_value="string code content")
        m = type("GenNodeModule", (object,), node or {})()
        mock = mocker.patch("parse.node_parser.ModuleFileLoader")
        mock.return_value.module = m
        mock.return_value.version = m.version if hasattr(m, "version") else "v1"

    return patch


def test_parse_should_log_warning_if_no_modules_found(mock_loader, caplog):
    mock_loader([])
    NodeParser("/test/path").parse()
    assert "No generation node file found" in caplog.text


def test_parse_should_use_filename_if_name_not_provided(mock_loader):
    mock_loader(["test.gen.py"], {"runs": [conf]})
    parsed = NodeParser("/test/path").parse()
    assert GenRun.create_key("test", 0) in parsed


def test_parse_should_use_provided_name_instead_of_filename(mock_loader):
    mock_loader(["test.gen.py"], {"name": "provided", "runs": [conf]})
    parsed = NodeParser("/test/path").parse()
    assert GenRun.create_key("provided", 0) in parsed


def test_parse_should_use_provided_version_instead_of_file_hash(mock_loader):
    mock_loader(["test.gen.py"], {"version": "provided", "runs": [conf]})
    parsed = NodeParser("/test/path").parse()
    assert parsed[GenRun.create_key("test", 0)].node_version == "provided"


def test_parse_should_wait_previous_runs(mock_loader):
    runs = [{**conf, "wait": ["node1/0"]}, {**conf, "wait": ["node2"]}]
    mock_loader(["test.gen.py"], {"runs": runs})
    parsed = NodeParser("/test/path").parse()

    first_run = parsed[GenRun.create_key("test", 0)]
    second_run = parsed[GenRun.create_key("test", 1)]
    assert first_run.run_key in second_run.wait


@pytest.mark.parametrize(
    "runs, expect",
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
def test_parse_raise_error_if_module_not_valid(mock_loader, runs, expect):
    mock_loader(["test.gen.py"], {"runs": runs})
    with pytest.raises(AssertionError) as err:
        NodeParser("/test/path").parse()
    assert expect in str(err.value)
