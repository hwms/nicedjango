
from collections import OrderedDict

from nicedjango.utils import iter_own_fields_with_name
from nicedjango.utils.fields import get_pk_name


class Relation(object):

    def __init__(self, node, name, rel_node, rel_name, to_pk=False,
                 to_dep=False):
        self.node = node
        self.name = name
        self.rel_node = rel_node
        self.rel_name = rel_name
        self.to_pk = to_pk
        self.to_dep = to_dep
        self.to_self = node == rel_node
        self.to_child = to_pk and not to_dep
        self.to_parent = to_pk and to_dep
        self.to_foreign = not to_pk and not to_dep

    def __str__(self):
        to_str = {(1, 1): 'parent', (1, 0): 'child', (0, 1): 'dependency',
                  (0, 0): 'foreign'}[(self.to_pk, self.to_dep)]
        to_str = self.to_self and 'self' or to_str
        return '%10s.%-10s to %-10s %10s.%s' % (self.node.label, self.name, to_str,
                                                self.rel_node.label, self.rel_name)

    def __repr__(self):
        return '<%s<%s>>' % (self.__class__.__name__, self)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and hash(self) == hash(other)

    def __hash__(self):
        return hash((self.node, self.name, self.rel_node, self.rel_name))


def get_relations(node):
    model, graph = node.model, node.graph
    relations = OrderedDict()
    for name, field, direct, m2m, is_rel in iter_own_fields_with_name(model):
        if not is_rel:
            continue
        to_dep = direct and not m2m
        to_pk = field.primary_key
        rm, rfn = _get_related_field_model_and_name(name, field, direct, m2m)
        rn = graph.get_node(rm)
        relations[name] = Relation(node, name, rn, rfn, to_pk, to_dep)
    return relations


def _get_related_field_model_and_name(name, field, direct, m2m):
    rfn = field.name
    rm = field.model
    if m2m:
        rm = field.rel.through
        rfn = field.m2m_reverse_field_name()
    elif direct:
        rfn = field.rel.get_related_field().name
        rm = field.rel.to
    rf, _, _, _ = rm._meta.get_field_by_name(rfn)
    if rf == rm._meta.pk:
        rfn = get_pk_name(rm)
    return rm, rfn
