import pytest

from util.graph_analyzer import GraphAnalyzer


def test_dependencies_should_return_correct_run_ids():
    n1, n2, n3, n4 = (("n1", ["n3"]), ("n2", ["n1", "n3"]), ("n3", []), ("n4", ["n2"]))
    analyzer = GraphAnalyzer([n1, n2, n3, n4])
    deps = analyzer.dependencies(n2[0])
    assert deps == [n3[0], n1[0], n2[0]]


def test_execution_order_should_raise_error_if_cyclic_dependencies_exists():
    n1, n2, n3 = (("n1", ["n3"]), ("n2", ["n1"]), ("n3", ["n2"]))
    analyzer = GraphAnalyzer([n1, n2, n3])
    with pytest.raises(AssertionError) as err:
        analyzer.execution_order()
    assert "Found cyclic dependencies" in str(err.value)


def test_execution_order_should_return_run_ids_in_correct_order():
    n1, n2, n3, n4 = (("n1", ["n3"]), ("n2", ["n1", "n3"]), ("n3", []), ("n4", ["n2"]))
    analyzer = GraphAnalyzer([n1, n2, n3, n4])
    order = analyzer.execution_order()
    assert order == [n3[0], n1[0], n2[0], n4[0]]
