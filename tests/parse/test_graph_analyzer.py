import pytest

from lokii.parse.graph_analyzer import GraphAnalyzer
from tests.conftest import mock_gen_run as mgr


def test_dependencies_should_return_correct_run_ids():
    r1, r2, r3 = mgr(n="n1", w=["n3"]), mgr(n="n2"), mgr(n="n3", w=["n2"])
    analyzer = GraphAnalyzer([r1, r2, r3])
    deps = analyzer.dependencies(r1.run_key)
    assert r3.run_key in deps
    assert r2.run_key in deps


def test_execution_order_should_raise_error_if_cyclic_dependencies_exists():
    r1, r2 = mgr(n="n1", w=["n2"]), mgr(n="n2", w=["n1"])
    analyzer = GraphAnalyzer([r1, r2])
    with pytest.raises(AssertionError) as err:
        analyzer.execution_order()
    assert "Found cyclic dependencies" in str(err.value)


def test_execution_order_should_return_run_ids_in_correct_order():
    r1, r2, r3 = mgr(n="n1", w=["n3"]), mgr(n="n2", w=["n1", "n3"]), mgr(n="n3")
    analyzer = GraphAnalyzer([r1, r2, r3])
    order = analyzer.execution_order()
    assert order == [r3.run_key, r1.run_key, r2.run_key]
