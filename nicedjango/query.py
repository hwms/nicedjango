__all__ = ['Query']


class Query(object):

    def __init__(self, node, queryset, pks=None, pk_field='pk'):
        self.node = node
        self.queryset = queryset
        self.pks = set(pks or [])
        self.pk_field = pk_field
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
        queryset = self.queryset
        if self.pks:
            filters = {'%s__in' % self.pk_field: self.pks}
            queryset = queryset.filter(**filters)
        deps = [(self.pk_field, self.node, None)] + list(self.node.deps)
        fields, nodes, _ = zip(*deps)
        queryset = list(queryset.values_list(*fields))
        result = zip(fields, nodes, zip(*queryset))
        return result

    def update_pks(self):
        for field, node, pks in self._get_pks_lists():
            # prevent pk query when comming from initial one
            no_new_query = not self.pks and field == self.pk_field
            node.add_pks(pks, no_new_query=no_new_query)
