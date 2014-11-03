import logging
from collections import defaultdict

from django.core import serializers
from django.db.models.fields.related import RelatedField
from django.db.models.related import RelatedObject

from nicedjango.utils import chunked, OrderedDict

log = logging.getLogger(__name__)

__all__ = ['Node']


class Node(object):
    def __init__(self, graph, model, label):
        self.graph = graph
        self.model = model
        self.meta = model._meta
        self.label = label

        self.deps = OrderedDict()
        self.related = defaultdict(set)

        self.pks = set()

    def init(self):
        for field in self.iter_own_related_fields():
            other = field.rel.to
            node = self.graph.get_node(other)
            self.deps[field.name] = node

        for rel in self.iter_own_related_objects():
            other = rel.model
            node = self.graph.get_node(other)
            self.related[node].add(rel.field.name)

    def iter_own_related(self):
        for name in self.meta.get_all_field_names():
            rel, model, _, _ = self.meta.get_field_by_name(name)
            if not model:
                yield rel

    def iter_own_related_fields(self):
        for field in self.iter_own_related():
            if isinstance(field, RelatedField) and issubclass(self.model,
                                                              field.rel.to):
                yield field

    def iter_own_related_objects(self):
        for rel in self.iter_own_related():
            if isinstance(rel, RelatedObject):
                yield rel

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

    def add_pks(self, pks, create_own_query=True):
        for node in [self] + list(self.deps.values()):
            new_pks = pks - node.pks
            if new_pks:
                node.pks.update(new_pks)
                if create_own_query:
                    self.graph.add_pk_query(node, pks=new_pks)
                for related, names in node.related.items():
                    for name in names:
                        self.graph.add_pk_query(related, fieldname=name,
                                                pks=new_pks)

    def dump_objects(self, outfile):
        pk_count = len(self.pks)
        chunks_count = int(pk_count / 10000) + 1
        for chunk_index, pks in enumerate(chunked(self.pks, 10000)):
            log.info('dumping chunk %d/%d of %s' % (chunk_index + 1,
                                                    chunks_count,
                                                    self.label))
            queryset = self.model.objects.filter(pk__in=pks)

            # TODO: write own json/p serializer able to dump and load in chunks
            # with one file, for now only yaml works with appending.
            s = serializers.serialize('yaml', queryset, indent=True,
                                      use_natural_keys=True)
            outfile.write(s)

    def dump_object(self):
        pass
