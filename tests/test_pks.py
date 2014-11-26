import pytest

from nicedjango.graph.graph import ModelGraph
from nicedjango.graph.utils import sort_nodes
from tests.samples_pks import SAMPLES_PKS


class DummyGraph(ModelGraph):

    def __init__(self, *args, **kwargs):
        super(DummyGraph, self).__init__(*args, **kwargs)
        self.all_pks_logs = []
        self.log_index = 0

    def get_new_pks_nodes(self):
        nodes = super(DummyGraph, self).get_new_pks_nodes()
        if nodes:
            pks_log = []
            new_pks_log = []
            for node in sort_nodes(self.nodes.values()):
                if node.pks:
                    prefix = not pks_log and 'pks_%d' % self.log_index or '     '
                    pks_log.append('%s %-19s %s' % (prefix, node.label,
                                                    ' '.join(sorted(map(str, node.pks)))))
                for name, new_pks in node.new_pks.items():
                    if new_pks:
                        prefix = not new_pks_log and 'new_%d' % self.log_index or '      '
                        new_pks_log.append('%s %-6s.%-12s %s' % (prefix, node.label, name,
                                                                 ' '.join(sorted(map(str,
                                                                                     new_pks)))))
            self.all_pks_logs.extend(pks_log)
            if new_pks_log:
                self.all_pks_logs.extend(new_pks_log)
            self.log_index += 1

        return nodes


@pytest.mark.django_db
@pytest.mark.graph(expected_no_nl=SAMPLES_PKS)
def test(test_id, queries, relations, expected):
    graph = DummyGraph(queries, relations)
    graph.update_pks()
    actual = '\n'.join(graph.all_pks_logs)
    # print('\n_____\n%s\n-----\n%s\n=====\n' % (test_id, actual))
    assert expected == actual
