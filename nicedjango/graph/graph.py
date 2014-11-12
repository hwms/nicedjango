from __future__ import print_function

import logging
from operator import attrgetter

from django.core import serializers
from django.db.models.loading import get_app, get_models
from django.db.models.query import QuerySet

from nicedjango._compat import basestring
from nicedjango.graph.node import Node
from nicedjango.graph.query import Query
from nicedjango.utils import (coerce_tuple, divide_model_def, model_label,
                              queryset_from_def, RememberingSet)

log = logging.getLogger(__name__)

__all__ = ['ModelGraph']


class ModelGraph(object):

    def __init__(self, queries=None, extras=None, app=None):
        self.nodes = {}
        self.extras = set()
        self.sorted_nodes = []
        self._new_nodes = RememberingSet()
        self._new_queries = RememberingSet()
        self.initial_querystrings = []
        if app:
            if queries or extras:
                raise ValueError('queries or extras can\'t be defined together'
                                 'with app.')
            app = get_app(app)
            queries = get_models(app, include_auto_created=True)
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
            log.debug(
                '%s %s %s' %
                (node.label, query.pk_field, len(
                    query.pks)))
            self._new_queries.add(query)

    def add_queries(self, *args):
        for arg in args:
            self.add_query(arg)

    def as_string(self):
        self.reset_sorted_notes()
        lines = []
        for node in self.sorted_nodes:
            nl = node.as_lines()
            if nl:
                lines.extend(nl)
        return '\n'.join(lines)

    def show(self):
        print(self.as_string())  # pragma: no cover

    def reset_sorted_notes(self):
        self.sorted_nodes = []
        to_order = set(self.nodes.values())
        found_one = True
        while to_order and found_one:
            found_one = False
            for node in sorted(to_order):
                can_be_added = True
                for conn in node.deps | node.pars:
                    if (conn.node != node
                            and conn.node not in self.sorted_nodes):
                        can_be_added = False
                        break
                if can_be_added:
                    self.sorted_nodes.append(node)
                    to_order.discard(node)
                    found_one = True

        if to_order:
            # should never happen, just to be safe
            raise ValueError('Failed to order circular'  # pragma: no cover
                             ' nodes: %s' % to_order)  # pragma: no cover

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
            model, name = divide_model_def(conn_def)
            node = self.get_node(model)
            related_infos = node.related_infos.get(name)
            if not related_infos:
                raise ValueError('Failed to get field by %s' % conn_def)
            self.extras.add((node, name))

    def load_objects(self, stream_or_string):
        node = None
        names = None
        values_list = []
        for obj in serializers.deserialize('compact_yaml', stream_or_string):
            actual_node = self.get_node(obj.model)
            if actual_node != node:
                if values_list:
                    node.update_or_create_objects(names, values_list)
                    values_list = []
                node = actual_node
                names = obj.names

            values_list.append(obj.values)
            if len(values_list) >= 100:
                node.update_or_create_objects(names, values_list)
                values_list = []
        if values_list:
            node.update_or_create_objects(names, values_list)
