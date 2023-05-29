import pytest

from lokii.model.node_module import GenRun, GenRunConf
from lokii.parse.graph_analyzer import GraphAnalyzer

conf: GenRunConf = {"source": "SELECT 1", "wait": [], "func": lambda x: x}


# noinspection PyTypeChecker
def test_dependencies_should_return_correct_run_ids():
    r1, r2, r3 = (
        GenRun("n1", "v1", 0, {**conf, "wait": ["n3"]}),
        GenRun("n2", "v1", 0, {**conf, "wait": []}),
        GenRun("n3", "v1", 0, {**conf, "wait": ["n2"]}),
    )
    analyzer = GraphAnalyzer([r1, r2, r3])
    deps = analyzer.dependencies(r1.run_key)
    assert r3.run_key in deps
    assert r2.run_key in deps


# noinspection PyTypeChecker
def test_execution_order_should_raise_error_if_cyclic_dependencies_exists():
    r1, r2 = (
        GenRun("n1", "v1", 0, {**conf, "wait": ["n2"]}),
        GenRun("n2", "v1", 0, {**conf, "wait": ["n1"]}),
    )
    analyzer = GraphAnalyzer([r1, r2])
    with pytest.raises(AssertionError) as err:
        analyzer.execution_order()
    assert "Found cyclic dependencies" in str(err.value)


# noinspection PyTypeChecker
def test_execution_order_should_return_run_ids_in_correct_order():
    r1, r2, r3 = (
        GenRun("n1", "v1", 0, {**conf, "wait": ["n3"]}),
        GenRun("n2", "v1", 0, {**conf, "wait": ["n1", "n3"]}),
        GenRun("n3", "v1", 0, {**conf, "wait": []}),
    )
    analyzer = GraphAnalyzer([r1, r2, r3])
    order = analyzer.execution_order()
    assert order == [r3.run_key, r1.run_key, r2.run_key]
