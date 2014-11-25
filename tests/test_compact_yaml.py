from __future__ import unicode_literals

from textwrap import dedent

import pytest
from django.utils import six

from nicedjango.graph.graph import ModelGraph
from tests.samples import reset_samples, SAMPLES
from tests.samples_compact_python import SAMPLES_PYTHON
from tests.samples_compact_yaml import SAMPLES_YAML
from tests.utils import delete_all, get_pydump, get_sorted_models, get_text_pydump


@pytest.mark.django_db
@pytest.mark.parametrize(('key'), SAMPLES.keys())
def test_compact_yaml(key):
    reset_samples()
    queries, relations = SAMPLES[key]
    graph = ModelGraph(queries, relations)
    sorted_models = get_sorted_models(graph.nodes.values())
    expected = dedent(SAMPLES_YAML[key])

    stream = six.StringIO()
    graph.dump_to_single_stream('compact_yaml', stream)

    actual = stream.getvalue()
    # print '*******'
    # print key
    # print actual
    # print '*******'
    assert expected == actual

    delete_all()
    graph = ModelGraph()
    stream.seek(0)
    graph.load_from_single_stream('compact_yaml', stream)

    expected = dedent(SAMPLES_PYTHON[key])[:-1]
    actual = get_text_pydump(get_pydump(sorted_models))
    assert expected == actual
