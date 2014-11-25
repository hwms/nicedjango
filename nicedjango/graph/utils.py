from operator import attrgetter

from nicedjango.utils import filter_attrs


def nodes_as_string(nodes):
    sort_key = attrgetter('to_dep', 'to_pk', 'name')
    lines = []
    for node in sort_nodes(nodes):
        if node.includes or node.excludes:
            lines.append('%s:' % node.label)
        for title, rels in ((None, node.includes),
                            ('excludes', node.excludes)):
            node_lines = list(map(lambda r: '    %s' % r,
                                  sorted(rels, key=sort_key)))
            if node_lines:
                if title:
                    lines.append('  %s:' % title)
                lines.extend(node_lines)
    return '\n'.join(lines)


def sort_nodes(nodes):
    sorted_nodes = []
    to_order = set(nodes)
    found_one = True
    while to_order and found_one:
        found_one = False
        for node in sorted(to_order):
            can_be_added = True
            for rel in filter_attrs(node.includes, to_dep=True, to_self=False):
                if rel.rel_node not in sorted_nodes:
                    can_be_added = False
                    break
            if can_be_added:
                sorted_nodes.append(node)
                to_order.discard(node)
                found_one = True
    if to_order:
        raise ValueError('Failed to order circular'  # pragma: no cover
                         ' nodes: %s' % to_order)  # pragma: no cover
    return sorted_nodes
