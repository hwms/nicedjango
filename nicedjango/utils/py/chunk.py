from __future__ import absolute_import

from collections import Sized
from itertools import groupby
from time import time

from nicedjango._compat import izip_longest

__all__ = ['as_chunks', 'sliceable_as_chunks', 'chunked', 'with_progress']

_marker = object()


class Progress(object):

    def __init__(self, pos, size, duration=0):
        super(Progress, self).__init__()
        self.pos = pos
        self.size = size
        self.duration = duration


class Chunk(Progress, list):

    def __init__(self, values, cpos, csize, pos, size, duration=0):
        super(Chunk, self).__init__(pos, size, duration)
        self.extend(values)
        self.cpos = cpos
        self.csize = csize
        self.len = len(self)
        self.to_pos = pos + self.len - 1
        self.per_obj = duration / self.len


def with_progress(iterable):
    size = 0
    if isinstance(iterable, Sized):
        size = len(iterable)
    start = time()
    for index, value in enumerate(iterable):
        duration = time() - start
        yield Progress(index + 1, size, duration), value


def as_chunks(iterable, n=1, key=None, chunk_value=None):
    size = 0
    csize = 0
    if isinstance(iterable, Sized):
        size = len(iterable)
        csize = int(size / n) + (size % n and 1)
    pos = 1
    cpos = 1
    start = time()
    for chunk in chunked(iterable, n):
        if chunk_value:
            chunk = chunk_value(chunk)
        duration = time() - start
        csize -= 1
        for key_chunk in chunk_as_chunks_by_key(chunk, key, pos, cpos, start,
                                                duration, csize + 1, size):
            yield key_chunk
            pos = key_chunk.to_pos + 1
            cpos += 1
            csize += 1


def sliceable_as_chunks(sliceable, n=1, key=None, chunk_value=None):
    pos = 1
    cpos = 1
    key_chunk = None
    while True:
        chunk = sliceable[pos - 1:pos - 1 + n]
        if not chunk:
            break
        if chunk_value:
            chunk = chunk_value(chunk)
        for key_chunk in chunk_as_chunks_by_key(chunk, key, pos, cpos):
            yield key_chunk

        pos = key_chunk.to_pos + 1
        cpos = key_chunk.cpos + 1


def chunk_as_chunks_by_key(main_chunk, key=None, pos=1, cpos=1, start=None,
                           duration=None, csize=0, size=0):
    if start is None:
        start = time()
    if not isinstance(main_chunk, Sized):
        main_chunk = list(main_chunk)
    if duration is None:
        duration = time() - start
    main_len = len(main_chunk)
    for key, values in key and groupby(main_chunk, key) or [(None, main_chunk)]:
        values = list(values)
        key_duration = duration or 0 and len(values) * duration / main_len
        chunk = Chunk(values, cpos, csize, pos, size, key_duration)
        yield chunk
        pos = chunk.to_pos + 1
        cpos = chunk.cpos + 1


def chunked(iterable, n):
    """
    Break an iterable into lists of a given length::
        >>> list(chunked([1, 2, 3, 4, 5, 6, 7], 3))
        [[1, 2, 3], [4, 5, 6], [7]]

    Copied from more_itertools:
        https://github.com/erikrose/more-itertools
    """
    for group in (list(g) for g in izip_longest(*[iter(iterable)] * n, fillvalue=_marker)):
        if group[-1] is _marker:
            # If this is the last group, shuck off the padding:
            del group[group.index(_marker):]
        yield group
