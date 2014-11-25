from __future__ import absolute_import

from collections import Callable

__all__ = ['get_or_create', 'RememberingSet']


class RememberingSet(set):

    def __init__(self, *args, **kwargs):
        super(RememberingSet, self).__init__(*args, **kwargs)
        self._memory = set()

    def add(self, value):
        if value not in self._memory and value not in self:
            super(RememberingSet, self).add(value)
            self._memory.add(value)

    def clear_memory(self):
        self._memory.clear()


NOT_SET = object()


def get_or_create(dct, key, value_or_callable, *default_args, **default_kwargs):
    value = dct.get(key, NOT_SET)
    if value is not NOT_SET:
        return value
    value = value_or_callable
    if isinstance(value, Callable):
        value = value(*default_args, **default_kwargs)
    dct[key] = value
    return value
