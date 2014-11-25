from __future__ import absolute_import

from collections import Iterable

__all__ = ['coerce_tuple']


def coerce_tuple(arg, *excludes):
    """
    If the argument *arg* is:
    * None, return empty tuple
    * an Iterable but not instance of *excludes*, by default (basestring,)
    * anything else as one element tuple
    """
    excludes = excludes or (basestring,)
    if arg is None:
        result = ()
    elif isinstance(arg, Iterable) and not isinstance(arg, excludes):
        result = tuple(arg)
    else:
        result = (arg,)
    return result
