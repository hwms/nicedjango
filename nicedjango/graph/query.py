import logging
from _collections import defaultdict

from nicedjango.utils import chunked

log = logging.getLogger(__name__)

__all__ = ['Query']


class Query(object):

    def __init__(self, node, queryset, pks=None, pk_field=None):
        self.node = node
        self.queryset = queryset
        self.pks = set(pks or [])
        self.pk_field = pk_field or node.pk_field
        self.hash = None
        self.update_hash()

    def update_hash(self):
        self.hash = hash((self.node.label, hash(self.queryset.query),
                          str(sorted(self.pks)), self.pk_field))

    def __eq__(self, other):
        return isinstance(other, Query) and self.hash == other.hash

    def __hash__(self):
        return self.hash

    def _get_pks_lists(self):
        deps = [(self.node.pk_field, self.node, None)] + list(self.node.deps)
        fields, nodes, _ = zip(*deps)
        queryset = self.queryset.values_list(*fields)
        pks_list = []
        if self.pks:
            pk_count = len(self.pks)
            chunks_count = int(pk_count / 100) + 1
            for chunk_index, pks in enumerate(chunked(self.pks, 100)):
                filters = {'%s__in' % self.pk_field: pks}
                log.info('loading %s by %s chunk %d/%d (%d)'
                         % (self.node.label, self.pk_field,
                            chunk_index + 1, chunks_count, len(pks)))
                pks_list.extend(queryset.filter(**filters))
        else:
            pks_list.extend(queryset)
        result = defaultdict(set)
        for pks_row in pks_list:
            for field, node, pk in zip(fields, nodes, pks_row):
                result[(field, node)].add(pk)
        return result

    def update_pks(self):
        pks_lists = self._get_pks_lists()
        for (field, node), pks in pks_lists.items():
            # prevent pk query when comming from initial one
            no_new_query = not self.pks and field == self.pk_field
            node.add_pks(pks, no_new_query=no_new_query)
