import logging
from collections import defaultdict
from operator import attrgetter

from django.core import serializers
from django.db.models.loading import get_model

from nicedjango.node import Node
from nicedjango.query import Query
from nicedjango.utils import model_label

log = logging.getLogger(__name__)

__all__ = ['ModelGraph']


class ModelGraph(object):
    def __init__(self):
        self.nodes = {}
        self.sorted_nodes = []
        self._new_nodes = set()
        self.initital_queries = defaultdict(set)
        self._new_pk_queries = set()

    def get_node(self, model):
        label = model_label(model)
        node = self.nodes.get(label, None)
        if not node:
            node = Node(self, model, label)
            self.nodes[label] = node
            self._new_nodes.add(node)
        return node

    def add_node(self, model):
        node = self.get_node(model)
        while self._new_nodes:
            self._new_nodes.pop().init()
        return node

    def add_querysets(self, *querysets):
        for queryset in querysets:
            self.add_queryset(queryset)

    def add_queryset(self, queryset):
        node = self.add_node(queryset.model)
        query = self.add_pk_query(node, queryset)
        self.initital_queries[node].add(query)

    def reset_sorted_notes(self):
        self.sorted_nodes = []
        nodes_to_order = set(self.nodes.values())
        while nodes_to_order:
            for node in sorted(nodes_to_order):
                can_be_added = True
                for other in node.deps.values():
                    if other != node and other not in self.sorted_nodes:
                        can_be_added = False
                        break
                if can_be_added:
                    self.sorted_nodes.append(node)
                    nodes_to_order.discard(node)

    def add_pk_query(self, node, queryset=None, pks=None, fieldname=None):
        query = Query(node, queryset, pks, fieldname)
        self._new_pk_queries.add(query)
        return query

    def update_pks(self):
        while self._new_pk_queries:
            self._new_pk_queries.pop().update_pks()

    def dump_objects(self, outfile, *queryset_defs):
        for queryset_def in queryset_defs:
            self.add_queryset_def(queryset_def)
        self.update_pks()
        self.reset_sorted_notes()
        sorted_nodes = list(filter(attrgetter('pks'), self.sorted_nodes))
        nodes_count = len(sorted_nodes)
        for node_index, node in enumerate(sorted_nodes):
            log.info('dumping %d/%d models: %s' % (node_index + 1, nodes_count,
                                                   node.label))
            node.dump_objects(outfile)

    def add_queryset_def(self, queryset_def):
        app, model_name, filter_def = queryset_def.split('-', 2)
        model = get_model(app, model_name)
        assert model
        # use eval to not go down the rabbithole to redefine djangos dsl here.
        queryset = eval('model.objects.%s' % filter_def)
        self.add_queryset(queryset)

    def load_objects(self, infile):
        for o in serializers.deserialize('yaml', infile):
            o.save()
