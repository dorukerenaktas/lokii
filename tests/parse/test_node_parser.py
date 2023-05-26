import pytest

from lokii.model.gen_module import GenRun, GenNodeModule as Gm
from lokii.parse.node_parser import NodeParser

# noinspection SpellCheckingInspection
pytestmark = [pytest.mark.usefixtures("found_mods", "loaded_mods")]


# noinspection SpellCheckingInspection, PyTestParametrized
@pytest.mark.parametrize("found_mods, loaded_mods", [([], [])], indirect=True)
def test_parse_should_log_warning_if_no_modules_found(caplog):
    NodeParser("/test/path").parse()
    assert "No generation node file found" in caplog.text


# noinspection SpellCheckingInspection, PyTestParametrized, PyTypeChecker
@pytest.mark.parametrize(
    "found_mods, loaded_mods", [(["t1"], [Gm([{}], None)])], indirect=True
)
def test_parse_should_use_filename_if_name_not_provided(found_mods):
    parsed = NodeParser("/test/path").parse()
    for module_path in found_mods:
        node_name = module_path.replace(".gen.py", "")
        run_key = GenRun.create_key(node_name, 0)
        # expect provided filename is used for parsed gen runs
        assert node_name == parsed[run_key].node_name
        assert run_key == parsed[run_key].run_key


# noinspection SpellCheckingInspection, PyTestParametrized, PyTypeChecker
@pytest.mark.parametrize(
    "found_mods, loaded_mods", [(["t1"], [Gm([{}], name="pt1")])], indirect=True
)
def test_parse_should_use_name_instead_of_filename(found_mods, loaded_mods):
    parsed = NodeParser("/test/path").parse()
    for i, module_path in enumerate(found_mods):
        mod = loaded_mods[i]
        run_key = GenRun.create_key(mod.name, 0)
        # expect provided module name is used for parsed gen runs
        assert mod.name == parsed[run_key].node_name
        assert run_key == parsed[run_key].run_key


# noinspection SpellCheckingInspection, PyTestParametrized, PyTypeChecker
@pytest.mark.parametrize(
    "found_mods, loaded_mods", [(["t1"], [Gm([{}], version="pv1")])], indirect=True
)
def test_parse_should_use_version_instead_of_file_hash(found_mods, loaded_mods):
    parsed = NodeParser("/test/path").parse()
    for i, module_path in enumerate(found_mods):
        mod = loaded_mods[i]
        node_name = module_path.replace(".gen.py", "")
        run_key = GenRun.create_key(node_name, 0)
        # expect provided module version is used for parsed gen runs
        assert mod.version == parsed[run_key].node_version


# noinspection SpellCheckingInspection, PyTestParametrized, PyTypeChecker
@pytest.mark.parametrize(
    "found_mods, loaded_mods", [(["t1"], [Gm([{}, {}])])], indirect=True
)
def test_parse_should_wait_its_own_previous_runs(found_mods, loaded_mods):
    parsed = NodeParser("/test/path").parse()
    for i, module_path in enumerate(found_mods):
        mod = loaded_mods[i]
        node_name = module_path.replace(".gen.py", "")
        for j, r in enumerate(mod.runs):
            if j > 0:
                before_run_key = GenRun.create_key(node_name, j - 1)
                run_key = GenRun.create_key(node_name, j)
                assert before_run_key in parsed[run_key].wait


# noinspection SpellCheckingInspection, PyTestParametrized, PyTypeChecker
@pytest.mark.parametrize("found_mods", [["t1"]], indirect=True)
@pytest.mark.parametrize(
    "loaded_mods, expect",
    [
        ([Gm(None)], "`runs` configuration not found"),
        ([Gm("None")], "`runs` must be list"),
        ([Gm([])], "`runs` has no items"),
        ([Gm([{"source": []}])], "[`source`] must be str"),
        ([Gm([{"wait": ""}])], "[`wait`] must be list"),
        ([Gm([{"func": None}])], "[`func`] not found"),
        ([Gm([{"func": ""}])], "[`func`] must be function"),
        ([Gm([{"func": lambda x, y: x}])], "[`func`] must accept only one"),
    ],
    indirect=["loaded_mods"],
)
def test_parse_raise_error_if_module_not_valid(expect):
    with pytest.raises(AssertionError) as err:
        NodeParser("/test/path").parse()
    assert expect in str(err.value)
