try:
    from itertools import izip_longest
except ImportError:
    from itertools import zip_longest as izip_longest


__all__ = ['chunked', 'model_label']


def model_label(model):
    return u'%s.%s' % (model._meta.app_label, model._meta.object_name.lower())


_marker = object()


def chunked(iterable, n):
    """
    Break an iterable into lists of a given length::
        >>> list(chunked([1, 2, 3, 4, 5, 6, 7], 3))
        [[1, 2, 3], [4, 5, 6], [7]]
    If the length of ``iterable`` is not evenly divisible by ``n``, the last
    returned list will be shorter.
    This is useful for splitting up a computation on a large number of keys
    into batches, to be pickled and sent off to worker processes. One example
    is operations on rows in MySQL, which does not implement server-side
    cursors properly and would otherwise load the entire dataset into RAM on
    the client.

    Copied from more_itertools:
        https://github.com/erikrose/more-itertools
    """
    # Doesn't seem to run into any number-of-args limits.
    for group in (list(g) for g in izip_longest(*[iter(iterable)] * n,
                                                fillvalue=_marker)):
        if group[-1] is _marker:
            # If this is the last group, shuck off the padding:
            del group[group.index(_marker):]
        yield group
