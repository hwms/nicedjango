import logging
from collections import namedtuple
from operator import attrgetter

from django.core import serializers

from nicedjango.graph.bulk_creator import BulkValuesListCreator
from nicedjango.utils import (chunked, get_own_direct_fields_with_name,
                              get_own_related_infos)

log = logging.getLogger(__name__)

__all__ = ['Node']


Connection = namedtuple('Connection', 'field node rel_field')


class Node(object):

    def __init__(self, graph, model, label):
        self.graph = graph
        self.model = model
        self.meta = model._meta
        self.related_infos = get_own_related_infos(self.model)
        # TODO: deal with proxy default managers and dump only concrete model
        self.direct_fields = \
            get_own_direct_fields_with_name(model._meta.concrete_model)
        self.pk_field = self.meta.pk.name
        self.label = label

        self.pars = set()
        # target's models where the node.model is inherited from
        self.subs = set()
        # target's models where the node.model is base from (pk wise)
        self.deps = set()
        # targets that are dependencies for the node
        self.rels = set()
        # related nodes which are to be parsed
        self.ignored_subs = set()
        # not to be parsed sub nodes stored for graph.show
        self.ignored_rels = set()
        # not to be parsed related nodes stored for graph.show

        self.pks = set()
        # pks discovered for this model

        self.creator = None

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        return isinstance(other, Node) and self.label == other.label

    def __lt__(self, other):  # pragma: no cover
        return self.label < other.label

    def __le__(self, other):  # pragma: no cover
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):  # pragma: no cover
        return not (self.__lt__(other) or self.__eq__(other))

    def __ge__(self, other):  # pragma: no cover
        return not self.__lt__(other)

    def __ne__(self, other):  # pragma: no cover
        return not self.__eq__(other)

    def __repr__(self):  # pragma: no cover
        return r'<%s<%s>>' % (self.__class__.__name__, self.label)

    def as_lines(self):
        lines = []
        for title, conns in (('parents', self.pars), ('depends', self.deps),
                             ('subs', self.subs), ('relates', self.rels),
                             ('ignored subs', self.ignored_subs),
                             ('ignored rels', self.ignored_rels)):
            sub_lines = []
            for conn in conns:
                sub_lines.append('    %s.%s > %s' % (self.label, conn.field,
                                                     conn.node.label))
            if sub_lines:
                lines.append('  %s:' % title)
                lines.extend(sorted(sub_lines))
        if lines:
            return ['%s:' % self.label] + lines
        return lines

    def init(self):
        for name, (rel_model, rel_name, is_dep, is_rel_pk
                   ) in self.related_infos.items():
            add_node = True
            if is_dep:
                if is_rel_pk:
                    conns = self.pars
                else:
                    conns = self.deps
            else:
                if (self, name) in self.graph.extras:
                    if is_rel_pk:
                        conns = self.subs
                    else:
                        conns = self.rels
                else:
                    add_node = False
                    if is_rel_pk:
                        conns = self.ignored_subs
                    else:
                        conns = self.ignored_rels

            node = self.graph.get_node(rel_model)
            conns.add(Connection(name, node, rel_name))
            if add_node and node != self:
                self.graph.add_node(node)

    def add_pks(self, pks, no_new_query=False):
        pks = set(pks) - set([None])
        nodes_and_rel_fields = [(self, self.pk_field)
                                ] + list(map(attrgetter('node', 'rel_field'),
                                             self.pars))
        for node, rel_field in nodes_and_rel_fields:
            new_pks = pks - node.pks
            if new_pks:
                node.pks.update(new_pks)
                if not no_new_query:
                    self.graph.add_query(node, pk_field=rel_field, pks=new_pks)
                for conn in node.subs | node.rels:
                    self.graph.add_query(conn.node, pk_field=conn.rel_field,
                                         pks=new_pks)

    def dump_objects(self, outfile):
        pk_count = len(self.pks)
        chunks_count = int(pk_count / 100) + 1
        for chunk_index, pks in enumerate(chunked(self.pks, 100)):
            log.info('dumping chunk %d/%d (%d) of %s'
                     % (chunk_index + 1, chunks_count, len(pks), self.label))
            queryset = self.model.objects.filter(pk__in=pks)
            s = serializers.serialize('compact_yaml', queryset, indent=True,
                                      use_natural_keys=False, width=10000)
            outfile.write(s)

    def update_or_create_objects(self, fieldnames, values_list):
        log.info('Update or create %d %s' % (len(values_list), self.label))
        names = list(filter(lambda n: n in self.direct_fields, fieldnames))
        names_not_in = set(fieldnames) - set(names)
        if names_not_in:
            raise ValueError('Fields %s missing in model %s.'
                             % (names_not_in, self.label))
        fields = list(map(self.direct_fields.get, names))
        if not self.creator:
            self.creator = BulkValuesListCreator(self.model, fields)
        self.creator.update_or_create(values_list)
