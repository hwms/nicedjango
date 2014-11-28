import pytest

from nicedjango.graph.graph import ModelGraph
from tests.utils import delete_all, get_pydump, get_text_pydump, print_actual


@pytest.mark.django_db
@pytest.mark.graph
def test(test_id, queries, relations, expected_dump, graph, sorted_models):
    rows = []
    graph.dump_to_single_stream('compact_python', rows)
    actual_dump = get_text_pydump(rows)
    print_actual(test_id, actual_dump)
    assert expected_dump == actual_dump

    delete_all()
    ModelGraph().load_from_single_stream('compact_python', rows)

    actual_dump = get_text_pydump(get_pydump(sorted_models))
    assert expected_dump == actual_dump
