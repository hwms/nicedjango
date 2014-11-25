from __future__ import unicode_literals

import glob
import logging
import os
import tempfile
from textwrap import dedent

import pytest

from nicedjango.graph.graph import ModelGraph
from nicedjango.graph.loader import Loader
from tests.samples import reset_samples, SAMPLES
from tests.samples_compact_csv import SAMPLES_CSV
from tests.samples_compact_python import SAMPLES_PYTHON
from tests.utils import delete_all, get_pydump, get_sorted_models, get_text_pydump

log = logging.getLogger(__name__)


@pytest.mark.django_db
@pytest.mark.parametrize(('key'), SAMPLES.keys())
def test_compact_csv(key):
    reset_samples()
    queries, relations = SAMPLES[key]
    graph = ModelGraph(queries, relations)
    sorted_models = get_sorted_models(graph.nodes.values())
    expected = dedent(SAMPLES_CSV[key])
    path = tempfile.mkdtemp()
    graph.dump_to_path('compact_csv', path)
    loader = Loader(graph, 'compact_csv')
    expected_filepaths = loader.get_filepaths(path)
    actual_filepaths = glob.glob(os.path.join(path, '*.csv'))
    assert set(expected_filepaths) == set(actual_filepaths)

    actual = []
    for filepath in expected_filepaths:
        label = os.path.basename(filepath).split('.')[0]
        with open(filepath) as csv_file:
            actual.append('%s\n' % label)
            for line in csv_file:
                actual.append('    %s' % line)
    actual = ''.join(actual)
    # print '*******'
    # print key
    # print actual
    # print '*******'
    delete_all()
    graph = ModelGraph()
    graph.load_from_path('compact_csv', path)

    for filepath in actual_filepaths:
        os.remove(filepath)
    os.rmdir(path)
    assert expected == actual

    expected = dedent(SAMPLES_PYTHON[key])[:-1]
    actual = get_text_pydump(get_pydump(sorted_models))
    assert expected == actual
