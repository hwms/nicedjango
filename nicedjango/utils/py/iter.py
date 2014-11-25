from __future__ import absolute_import

from itertools import tee
from operator import attrgetter, itemgetter

from nicedjango._compat import filterfalse, imap

__all__ = ['filter_attrs', 'map_item', 'index_shift_map', 'partition']


def filter_attrs(objects, *attrs, **kwargs):
    for obj in objects:
        include = True
        for attr in attrs:
            if not getattr(obj, attr, None):
                include = False
                break
        if include:
            for attr, value in kwargs.items():
                if getattr(obj, attr) != value:
                    include = False
                    break
        if include:
            yield obj


def map_attr(objects, attr):
    return imap(attrgetter(attr), objects)


def map_item(index, values_list):
    return imap(itemgetter(index), values_list)


def index_shift_map(index, to, values_list, length=None):
    for values in values_list:
        values = list(values)
        values.insert(to, values.pop(index))
        yield values


def partition(pred, iterable):
    'Use a predicate to partition entries into false entries and true entries'
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)
