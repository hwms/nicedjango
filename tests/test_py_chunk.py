from nicedjango.utils.py.chunk import as_chunks, sliceable_as_chunks
from nicedjango.utils.py.iter import map_attr


def test_as_chunks_unsized():
    iterable = iter([1, 2, 3, 4, 5, 6, 7, 8, 9])
    chunks = list(as_chunks(iterable, 4))
    assert [[1, 2, 3, 4], [5, 6, 7, 8], [9]] == chunks
    assert [1, 2, 3] == list(map_attr(chunks, 'cpos'))
    assert [0, 0, 0] == list(map_attr(chunks, 'csize'))
    assert [1, 5, 9] == list(map_attr(chunks, 'pos'))
    assert [4, 8, 9] == list(map_attr(chunks, 'to_pos'))
    assert [0, 0, 0] == list(map_attr(chunks, 'size'))
    assert [4, 4, 1] == list(map_attr(chunks, 'len'))


def test_as_chunks_sized():
    iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    chunks = list(as_chunks(iterable, 4))
    assert [[1, 2, 3, 4], [5, 6, 7, 8], [9]] == chunks
    assert [1, 2, 3] == list(map_attr(chunks, 'cpos'))
    assert [3, 3, 3] == list(map_attr(chunks, 'csize'))
    assert [1, 5, 9] == list(map_attr(chunks, 'pos'))
    assert [4, 8, 9] == list(map_attr(chunks, 'to_pos'))
    assert [9, 9, 9] == list(map_attr(chunks, 'size'))
    assert [4, 4, 1] == list(map_attr(chunks, 'len'))


def test_sliceable_as_chunks():
    iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    chunks = list(sliceable_as_chunks(iterable, 4))
    assert [[1, 2, 3, 4], [5, 6, 7, 8], [9]] == chunks
    assert [1, 2, 3] == list(map_attr(chunks, 'cpos'))
    assert [0, 0, 0] == list(map_attr(chunks, 'csize'))
    assert [1, 5, 9] == list(map_attr(chunks, 'pos'))
    assert [4, 8, 9] == list(map_attr(chunks, 'to_pos'))
    assert [0, 0, 0] == list(map_attr(chunks, 'size'))
    assert [4, 4, 1] == list(map_attr(chunks, 'len'))


def test_as_chunks_chunk_value():
    iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    chunks = list(as_chunks(iterable, 4, chunk_value=lambda vs: map(str, vs)))
    assert [['1', '2', '3', '4'], ['5', '6', '7', '8'], ['9']] == chunks


def test_sliceable_as_chunks_chunk_value():
    iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    chunks = list(sliceable_as_chunks(iterable, 4, chunk_value=lambda vs: map(str, vs)))
    assert [['1', '2', '3', '4'], ['5', '6', '7', '8'], ['9']] == chunks


def test_as_chunks_key():
    iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    chunks = list(as_chunks(iterable, 4, key=lambda v: v % 4 == 0))
    assert [[1, 2, 3], [4], [5, 6, 7], [8], [9]] == chunks
    assert [1, 2, 3, 4, 5] == list(map_attr(chunks, 'cpos'))
    assert [3, 3, 4, 4, 5] == list(map_attr(chunks, 'csize'))
    assert [1, 4, 5, 8, 9] == list(map_attr(chunks, 'pos'))
    assert [3, 4, 7, 8, 9] == list(map_attr(chunks, 'to_pos'))
    assert [9, 9, 9, 9, 9] == list(map_attr(chunks, 'size'))
    assert [3, 1, 3, 1, 1] == list(map_attr(chunks, 'len'))


def test_sliceable_as_chunks_key():
    iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    chunks = list(sliceable_as_chunks(iterable, 4, key=lambda v: v % 4 == 0))
    assert [[1, 2, 3], [4], [5, 6, 7], [8], [9]] == chunks
    assert [1, 2, 3, 4, 5] == list(map_attr(chunks, 'cpos'))
    assert [0, 0, 0, 0, 0] == list(map_attr(chunks, 'csize'))
    assert [1, 4, 5, 8, 9] == list(map_attr(chunks, 'pos'))
    assert [3, 4, 7, 8, 9] == list(map_attr(chunks, 'to_pos'))
    assert [0, 0, 0, 0, 0] == list(map_attr(chunks, 'size'))
    assert [3, 1, 3, 1, 1] == list(map_attr(chunks, 'len'))
