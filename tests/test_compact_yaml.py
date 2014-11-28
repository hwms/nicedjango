from django.utils import six
import pytest

from nicedjango.graph.graph import ModelGraph
from tests.samples_compact_yaml import SAMPLES_YAML
from tests.utils import delete_all, get_text_pydump, get_pydump, print_actual


@pytest.mark.django_db
@pytest.mark.graph(expected=SAMPLES_YAML)
def test(test_id, queries, relations, expected, expected_dump, graph, sorted_models):
    stream = six.StringIO()
    graph.dump_to_single_stream('compact_yaml', stream)

    actual = stream.getvalue()
    print_actual(test_id, actual)
    assert expected == actual

    delete_all()
    stream.seek(0)
    ModelGraph().load_from_single_stream('compact_yaml', stream)

    actual_dump = get_text_pydump(get_pydump(sorted_models))
    assert expected_dump == actual_dump
