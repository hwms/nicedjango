import pytest

from nicedjango.utils import divide_model_def, model_label, queryset_from_def
from tests.a1.models import A
from tests.a2 import models as a2
from tests.a3.models import Book

DIVIDE_RESULTS = (
    (A, A, ''),
    ('a1-a', A, ''),
    ('a', A, ''),
    ('a1-a.foo.bar', A, 'foo.bar'),
    ('a.foo.bar', A, 'foo.bar'),
    (a2.Book, a2.Book, ''),
    ('a2-book', a2.Book, ''),
    ('a2-book.foo.bar', a2.Book, 'foo.bar'),
    (Book, Book, ''),
    ('a3-book', Book, ''),
    ('a3-book.foo.bar', Book, 'foo.bar'),
)
DIVIDE_RESULTS_IDS = list(map(lambda d: model_label(d[0]), DIVIDE_RESULTS))


@pytest.mark.parametrize(('model_def', 'model', 'rest'), DIVIDE_RESULTS,
                         ids=DIVIDE_RESULTS_IDS)
def test_divide_model_def(model_def, model, rest):
    actual = divide_model_def(model_def)
    assert actual == (model, rest)


DIVIDE_FAILS = (
    'article',
    'article.foo',
    'a1-foo.bar',
    'a1',
    'a1-foo',
    'a1-foo.bar',
    object())
DIVIDE_FAILS_IDS = list(map(model_label, DIVIDE_FAILS))


@pytest.mark.parametrize('model_def', DIVIDE_FAILS, ids=DIVIDE_FAILS_IDS)
def test_divide_model_def_fails(model_def):
    with pytest.raises(ValueError):
        divide_model_def(model_def)


ALL_QS = A.objects.all()
ALL_SQL = str(ALL_QS.query)
TEST_QS = A.objects.filter(id=1)
TEST_SQL = str(TEST_QS.query)

QS_DEF_RESULTS = (
    (ALL_QS, ALL_SQL),
    (A, ALL_SQL),
    ('a1-a', ALL_SQL),
    ('a', ALL_SQL),
    ('a1-a.all()', ALL_SQL),
    ('a.all()', ALL_SQL),
    (TEST_QS, TEST_SQL),
    ('a1-a.filter(id=1)', TEST_SQL),
    ('a.filter(id=1)', TEST_SQL)
)


@pytest.mark.parametrize(('queryset_def', 'expected_sql'), QS_DEF_RESULTS)
def test_queryset_from_def(queryset_def, expected_sql):
    queryset = queryset_from_def(queryset_def)
    assert str(queryset.query) == expected_sql
