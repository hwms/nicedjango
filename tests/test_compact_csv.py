import glob
import os

import pytest

from nicedjango.graph.graph import ModelGraph
from nicedjango.graph.loader import Loader
from tests.samples_compact_csv import SAMPLES_CSV
from tests.utils import delete_all, get_pydump, get_text_pydump


def read_files_into_indented_string(paths):
    lines = []
    for filepath in paths:
        label = os.path.basename(filepath).split('.')[0]
        with open(filepath) as csv_file:
            lines.append('%s\n' % label)
            for line in csv_file:
                lines.append('    %s' % line.decode('utf8'))
    return ''.join(lines)


@pytest.mark.django_db
@pytest.mark.graph(expected=SAMPLES_CSV)
def test(test_id, queries, relations, expected, expected_dump, graph, sorted_models, tmpdir):
    path = tmpdir.mkdir('csvs')
    pattern = path.join('*.csv').strpath
    path = path.strpath

    graph.dump_to_path('compact_csv', path)
    loader = Loader(graph, 'compact_csv')
    expected_filepaths = loader.get_filepaths(path)
    actual_filepaths = glob.glob(pattern)
    assert set(expected_filepaths) == set(actual_filepaths)

    actual = read_files_into_indented_string(expected_filepaths)
    # print('\n_____\n%s\n-----\n%s\n=====\n' % (test_id, actual))
    assert expected == actual

    delete_all()
    ModelGraph().load_from_path('compact_csv', path)
    actual_dump = get_text_pydump(get_pydump(sorted_models))
    assert expected_dump == actual_dump
