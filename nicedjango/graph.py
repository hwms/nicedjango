from __future__ import print_function

import logging
from operator import attrgetter

from django.core import serializers
from django.db.models.query import QuerySet
from nicedjango._compat import basestring
from nicedjango.node import Node
from nicedjango.query import Query
from nicedjango.utils import (coerce_tuple, get_related_object_from_def,
                              model_label, queryset_from_def, RememberingSet)

log = logging.getLogger(__name__)

__all__ = ['ModelGraph']


class ModelGraph(object):

    def __init__(self, queries=None, extras=None):
        self.nodes = {}
        self.extras = set()
        self.sorted_nodes = []
        self._new_nodes = RememberingSet()
        self._new_queries = RememberingSet()
        self.initial_querystrings = []
        self.add_extras(*coerce_tuple(extras, basestring, QuerySet))
        self.add_queries(*coerce_tuple(queries, basestring, QuerySet))

    def get_node(self, model):
        label = model_label(model)
        node = self.nodes.get(label, None)
        if not node:
            node = Node(self, model, label)
            self.nodes[label] = node
        return node

    def add_node(self, arg):
        if not isinstance(arg, Node):
            arg = self.get_node(arg)
        self._new_nodes.add(arg)
        while self._new_nodes:
            self._new_nodes.pop().init()
        return arg

    def add_query(self, arg, **kwargs):
        if isinstance(arg, Node):
            node = arg
            queryset = queryset_from_def(node.model)
        else:
            queryset = queryset_from_def(arg)
            node = self.add_node(queryset.model)

        query = Query(node, queryset, **kwargs)
        if query not in self._new_queries:
            log.warning('%s %s %s' % (node.label, query.pk_field, query.pks))
        self._new_queries.add(query)

    def add_queries(self, *args):
        for arg in args:
            self.add_query(arg)

    def as_string(self):
        lines = []
        for node in sorted(self.nodes.values()):
            nl = node.as_lines()
            if nl:
                lines.extend(nl)
        return '\n'.join(lines)

    def show(self):
        print(self.as_string())

    def reset_sorted_notes(self):
        self.sorted_nodes = []
        nodes_to_order = set(self.nodes.values())
        found_one = True
        while nodes_to_order and found_one:
            found_one = False
            for node in sorted(nodes_to_order):
                can_be_added = True
                for conn in node.deps:
                    if (conn.node != node
                            and conn.node not in self.sorted_nodes):
                        can_be_added = False
                        break
                if can_be_added:
                    self.sorted_nodes.append(node)
                    nodes_to_order.discard(node)
                    found_one = True

        if nodes_to_order:
            raise ValueError('Failed to order circular nodes: %s'
                             % nodes_to_order)

    def update_pks(self):
        while self._new_queries:
            self._new_queries.pop().update_pks()

    def dump_objects(self, outfile):
        self.update_pks()
        self.reset_sorted_notes()
        sorted_nodes = list(filter(attrgetter('pks'), self.sorted_nodes))
        nodes_count = len(sorted_nodes)
        for node_index, node in enumerate(sorted_nodes):
            log.info('dumping %d/%d models: %s' % (node_index + 1, nodes_count,
                                                   node.label))
            node.dump_objects(outfile)

    def add_extras(self, *conn_defs):
        for conn_def in conn_defs:
            robj = get_related_object_from_def(conn_def)
            node = self.get_node(robj.parent_model)
            self.extras.add((node, robj.var_name))

    def load_objects(self, infile):
        for o in serializers.deserialize('yaml', infile):
            o.save()
