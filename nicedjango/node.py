import logging
from collections import namedtuple
from operator import attrgetter

from django.core import serializers
from nicedjango.utils import chunked, get_own_related_infos

log = logging.getLogger(__name__)

__all__ = ['Node']


Connection = namedtuple('Connection', 'field node rel_field')


class Node(object):

    def __init__(self, graph, model, label):
        self.graph = graph
        self.model = model
        self.meta = model._meta
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

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        return isinstance(other, Node) and self.label == other.label

    def __lt__(self, other):
        return self.label < other.label

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return not (self.__lt__(other) or self.__eq__(other))

    def __ge__(self, other):
        return not self.__lt__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
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
        related_infos = get_own_related_infos(self.model)
        for field, rel_model, rel_field, is_pk, is_rel in related_infos:
            add_node = True
            if is_rel:
                if (self, field) in self.graph.extras:
                    conns = self.subs if is_pk else self.rels
                else:
                    add_node = False
                    conns = self.ignored_subs if is_pk else self.ignored_rels
            else:
                conns = self.pars if is_pk else self.deps

            node = self.graph.get_node(rel_model)
            conns.add(Connection(field, node, rel_field))
            if add_node and node != self:
                self.graph.add_node(node)

    def add_pks(self, pks, no_new_query=False):
        pks = set(pks) - set([None])
        nodes = [self] + list(map(attrgetter('node'), self.pars))
        for node in nodes:
            new_pks = pks - node.pks
            if new_pks:
                node.pks.update(new_pks)
                if not no_new_query:
                    self.graph.add_query(node, pks=new_pks)
                for conn in node.subs:
                    self.graph.add_query(conn.node, pk_field=conn.rel_field,
                                         pks=new_pks)
                if self.rels and node == self:
                    for conn in node.rels:
                        self.graph.add_query(conn.node,
                                             pk_field=conn.rel_field,
                                             pks=new_pks)

    def dump_objects(self, outfile):
        pk_count = len(self.pks)
        chunks_count = int(pk_count / 10000) + 1
        for chunk_index, pks in enumerate(chunked(self.pks, 10000)):
            log.info('dumping chunk %d/%d (%d) of %s'
                     % (chunk_index + 1, chunks_count, len(pks), self.label))
            queryset = self.model.objects.filter(pk__in=pks)
            # TODO: write own json/p serializer able to dump and load in chunks
            # with one file, for now only yaml works with appending.
            s = serializers.serialize('yaml', queryset, indent=True,
                                      use_natural_keys=False)
            outfile.write(s.encode('utf-8'))

    def dump_object(self):
        pass
