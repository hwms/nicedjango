from nicedjango.utils import get_or_create


def test_get_or_create():
    d = {}
    a = lambda *args, **kwargs: (args, kwargs)
    v = get_or_create(d, 'key', a, 1, b=2)
    expected_v = ((1,), {'b': 2})
    expected_d = {'key': expected_v}
    assert expected_v == v
    assert expected_d == d

    d = {}
    v = get_or_create(d, 'key', 'value')
    assert 'value' == v
    assert {'key': 'value'} == d

    d = {'key': 'value'}
    v = get_or_create(d, 'key', a, 1, b=2)
    assert 'value' == v
    assert {'key': 'value'} == d
