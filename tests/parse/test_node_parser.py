import pytest

from lokii.model.gen_module import GenRun
from lokii.parse.node_parser import NodeParser
from tests.conftest import mock_gen_conf as mgc


def test_parse_should_log_warning_if_no_modules_found(mock_module_loader, caplog):
    mock_module_loader([])
    NodeParser("/test/path").parse()
    assert "No generation node file found" in caplog.text


def test_parse_should_use_filename_if_name_not_provided(mock_module_loader):
    mock_module_loader(["test.gen.py"], {"runs": [mgc()]})
    parsed = NodeParser("/test/path").parse()
    assert GenRun.create_key("test", 0) in parsed


def test_parse_should_use_provided_name_instead_of_filename(mock_module_loader):
    mock_module_loader(["test.gen.py"], {"name": "provided", "runs": [mgc()]})
    parsed = NodeParser("/test/path").parse()
    assert GenRun.create_key("provided", 0) in parsed


def test_parse_should_use_provided_version_instead_of_file_hash(mock_module_loader):
    mock_module_loader(["test.gen.py"], {"version": "provided", "runs": [mgc()]})
    parsed = NodeParser("/test/path").parse()
    assert parsed[GenRun.create_key("test", 0)].node_version == "provided"


def test_parse_should_wait_previous_runs(mock_module_loader):
    runs = [mgc(w=["node1/0"]), mgc(w=["node2"])]
    mock_module_loader(["test.gen.py"], {"runs": runs})
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
        ([{"source": ""}], "[`func`] not found"),
        ([{"source": "", "func": ""}], "[`func`] must be function"),
        ([{"source": "", "func": lambda x, y: x}], "[`func`] must accept only one"),
    ],
)
def test_parse_raise_error_if_module_not_valid(mock_module_loader, runs, expect):
    mock_module_loader(["test.gen.py"], {"runs": runs})
    with pytest.raises(AssertionError) as err:
        NodeParser("/test/path").parse()
    assert expect in str(err.value)
