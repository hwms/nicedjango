from __future__ import print_function

from time import time

from django.core.serializers import register_serializer
from django.db.models.base import ModelBase
from django.db.models.loading import get_app, get_models
from django.db.models.query import QuerySet

from nicedjango._compat import basestring
from nicedjango.graph.dumper import Dumper
from nicedjango.graph.loader import Loader
from nicedjango.graph.node import Node
from nicedjango.graph.utils import nodes_as_string, sort_nodes
from nicedjango.utils import coerce_tuple, divide_model_def, queryset_from_def, RememberingSet
from nicedjango.utils.py.iter import filter_attrs
from nicedjango.utils.py.string import divide_string

register_serializer('compact_csv', 'nicedjango.serializers.compact_csv')
register_serializer('compact_python', 'nicedjango.serializers.compact_python')
register_serializer('compact_yaml', 'nicedjango.serializers.compact_yaml')

__all__ = ['ModelGraph']


class ModelGraph(object):

    def __init__(self, queries=None, relations=None, app=None, chunksize=1000):
        self.nodes = {}
        self.includes = set()
        self._new_nodes = RememberingSet()
        if app:
            if queries or relations:
                raise ValueError('queries or relations can\'t be defined '
                                 'together with app.')
            app = get_app(app)
            queries = get_models(app, include_auto_created=True)
        self.chunksize = chunksize
        self.add_relations(*coerce_tuple(relations, basestring, QuerySet))
        self.add_queries(*coerce_tuple(queries, basestring, QuerySet))

        self._start = time()

    def add_relations(self, *rel_defs):
        for rel_def in rel_defs:
            model_str, name = divide_string(rel_def, '.')
            model, _ = divide_model_def(model_str)
            node = self.get_node(model)
            self.includes.add((node, name))

    def add_queries(self, *args):
        for arg in args:
            self.add_queryset_def(arg)

    def add_queryset_def(self, queryset_def):
        queryset = queryset_from_def(queryset_def)
        self.add_node(queryset.model).new_querysets.append(queryset)

    def add_node(self, arg):
        if not isinstance(arg, Node):
            arg = self.get_node(arg)
        if arg.relations is None:
            self._new_nodes.add(arg)
        while self._new_nodes:
            self._new_nodes.pop().init()
        return arg

    def get_node(self, model):
        if not isinstance(model, ModelBase):
            model, _ = divide_model_def(model)
        node_ = Node(self, model)
        node = self.nodes.get(node_.label, None)
        if not node:
            node = node_
            self.nodes[node.label] = node
        return node

    def print_graph(self):
        print(nodes_as_string(self.nodes.values()))  # pragma: no cover

    def update_pks(self):
        for node in sort_nodes(self.nodes.values()):
            node.get_pks()
        nodes = self.get_new_pks_nodes()
        while nodes:
            for node in nodes:
                node.get_new_pks()
            nodes = self.get_new_pks_nodes()

    def get_new_pks_nodes(self):
        return list(filter_attrs(sort_nodes(self.nodes.values()), 'new_pks'))

    def get_dumper(self, serializer_name):
        self.update_pks()
        sorted_nodes = sort_nodes(self.nodes.values())
        return Dumper(sorted_nodes, serializer_name, self.chunksize)

    def dump_to_single_stream(self, serializer_name, stream):
        self.get_dumper(serializer_name).dump_to_single_stream(stream)

    def load_from_single_stream(self, serializer_name, stream):
        loader = Loader(self, serializer_name)
        loader.load_from_stream(stream)

    def dump_to_path(self, serializer_name, path):
        self.get_dumper(serializer_name).dump_to_path(path)

    def load_from_path(self, serializer_name, path):
        loader = Loader(self, serializer_name)
        loader.load_from_path(path)
