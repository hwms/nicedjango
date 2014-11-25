import logging
from collections import defaultdict

from nicedjango.graph.relation import get_relations
from nicedjango.utils import model_label
from nicedjango.utils.fields import get_pk_name
from nicedjango.utils.py.iter import filter_attrs
from nicedjango.utils.queries import queryset_as_chunks

log = logging.getLogger(__name__)

__all__ = ['Node']

LOG_FORMAT = 'Loading pks %s by %s chunk %%(cpos)d/%%(csize)d (%%(size)d)'


class Node(object):

    def __init__(self, graph, model):
        self.graph = graph
        self.model = model
        self.meta = model._meta
        self.label = model_label(model)
        self.pk_name = get_pk_name(model)
        self.relations = None
        self.includes = set()
        self.excludes = set()

        self.new_querysets = []
        self.pks = set()
        self.new_pks = defaultdict(set)

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        return isinstance(other, Node) and self.label == other.label

    def __lt__(self, other):  # pragma: no cover
        return self.label < other.label

    def __repr__(self):  # pragma: no cover
        return r'<%s<%s>>' % (self.__class__.__name__, self.label)

    def init(self):
        self.includes = set()
        self.excludes = set()
        self.deps = []
        self.deps_not_to_pk = []
        self.query_names = [self.pk_name]
        self.query_rel_nodes = [self]
        self.relations = get_relations(self)
        for relation in self.relations.values():
            if not (relation.to_dep or (self, relation.name) in self.graph.includes):
                self.excludes.add(relation)
                continue

            self.includes.add(relation)
            if not relation.to_self:
                self.graph.add_node(relation.rel_node)
            if relation.to_dep and relation not in self.deps:
                self.deps.append(relation)
                self.query_names.append(relation.name)
                self.query_rel_nodes.append(relation.rel_node)
                if not relation.to_pk and relation not in self.deps_not_to_pk:
                    self.deps_not_to_pk.append(relation)

    def get_pks(self):
        while self.new_querysets:
            self.get_pks_from_queryset(self.new_querysets.pop())

    def get_pks_from_queryset(self, queryset, rel_name=None, rel_pks=None):
        queryset = queryset.values_list(*self.query_names)
        for pks_chunk in queryset_as_chunks(queryset, self.graph.chunksize, rel_name, rel_pks):
            log.info(LOG_FORMAT % (self.label, rel_name), vars(pks_chunk))
            if not pks_chunk:
                raise ValueError('no pks returned: %s' % (queryset.query))
            self.get_pks_from_list(pks_chunk)

    def get_pks_from_list(self, pks_list):
        for pks_row in pks_list:
            for rel_node, rel_name, pk in zip(self.query_rel_nodes, self.query_names, pks_row):
                if pk is not None:
                    rel_node.add_pk(pk, self, rel_name)

    def add_pk(self, pk, from_node, name):
        if pk in self.pks or pk in self.new_pks[self.pk_name]:
            return
        if (from_node == self and name == self.pk_name) or not self.deps_not_to_pk:
            self.pks.add(pk)
            for other in filter_attrs(self.includes, to_dep=False):
                other.rel_node.new_pks[other.rel_name].add(pk)
            for parent in filter_attrs(self.includes, to_parent=True):
                parent.rel_node.add_pk(pk, parent.rel_node, parent.rel_node.pk_name)
        else:
            self.new_pks[self.pk_name].add(pk)

    def get_new_pks(self):
        if not self.new_pks:
            return
        while self.new_pks:
            name, new_pks = self.new_pks.popitem()
            if not new_pks:
                continue
            log.debug('%s %s', name, new_pks)
            self.get_pks_from_queryset(self.model._default_manager.all(), name, new_pks)
