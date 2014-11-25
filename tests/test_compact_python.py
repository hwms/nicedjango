from __future__ import unicode_literals

from textwrap import dedent

import pytest

from nicedjango.graph.graph import ModelGraph
from tests.samples import reset_samples, SAMPLES
from tests.samples_compact_python import SAMPLES_PYTHON
from tests.utils import delete_all, get_pydump, get_sorted_models, get_text_pydump


@pytest.mark.django_db
@pytest.mark.parametrize(('key'), SAMPLES.keys())
def test_compact_python(key):
    reset_samples()
    queries, relations = SAMPLES[key]
    graph = ModelGraph(queries, relations)
    sorted_models = get_sorted_models(graph.nodes.values())
    expected = dedent(SAMPLES_PYTHON[key])[:-1]

    rows = []
    graph.dump_to_single_stream('compact_python', rows)
    actual = get_text_pydump(rows)
    # print '*******'
    # print key
    # print actual
    # print '*******'
    assert expected == actual

    delete_all()
    graph = ModelGraph()
    graph.load_from_single_stream('compact_python', rows)

    actual = get_text_pydump(get_pydump(sorted_models))
    assert expected == actual
