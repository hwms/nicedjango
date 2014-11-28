import pytest

from tests.samples_relations import SAMPLES_RELATIONS
from tests.utils import print_actual


@pytest.mark.graph(expected_no_nl=SAMPLES_RELATIONS)
def test(test_id, expected, graph):
    actual = graph.relations_as_string()
    print_actual(test_id, actual)
    assert expected == actual
