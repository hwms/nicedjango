from collections import defaultdict, OrderedDict

__all__ = ['Query']


class Query(object):
    def __init__(self, node, queryset=None, pks=None, fieldname=None):
        self.node = node
        self.nodes = OrderedDict([('pk', self.node)])
        self.nodes.update(self.node.deps)
        self.queryset = queryset or node.model._default_manager.all()
        self.pks = pks
        self.fieldname = fieldname or 'pk' if self.pks else None

        self.hash = hash((self.node.label, str(self.queryset.query),
                          str(sorted(self.pks) if self.pks else ''),
                          self.fieldname))

    def __eq__(self, other):
        return isinstance(other, Query) and self.hash == other.hash

    def __hash__(self):
        return self.hash

    def get_pks_list(self):
        queryset = self.queryset
        if self.pks:
            queryset = queryset.filter(**{'%s__in' % self.fieldname: self.pks})
        return list(queryset.values_list(*self.nodes.keys()))

    def update_pks(self):
        pks_list = self.get_pks_list()
        per_node = defaultdict(set)
        for pks in pks_list:
            own_pk = pks[0]
            if own_pk in self.node.pks:
                continue
            for pk, node in zip(pks, self.nodes.values()):
                if pk is not None:
                    per_node[node].add(pk)
        for node, pks in per_node.items():
            node.add_pks(pks, create_own_query=bool(self.pks))
