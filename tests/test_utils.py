import pytest

from nicedjango.utils import (divide_model_def, get_own_related_infos,
                              model_label, queryset_from_def)
from tests.a1.models import A, B, C
from tests.a2.models import (Abstract, Foreign, ManyToMany, OneToOne, Proxy,
                             Real, Sub, SubSub)
from tests.a3 import models as a3
from tests.a4.models import Article, Book, BookReview, Piece

INFOS = (
    (A, [('b', B, 'a_ptr', True, True)]),
    (B, [('a_ptr', A, 'b', True, False), ('c', C, 'b_ptr', True, True)]),
    (C, [('b_ptr', B, 'c', True, False)]),

    (Abstract, []),
    (Real, [('foreign', Foreign, 'f', False, True),
            ('manytomany', ManyToMany, 'm', False, True),
            ('onetoone', OneToOne, 'r', False, True),
            ('sub', Sub, 'real_ptr', True, True)]),
    (Proxy, []),
    (Sub, [('real_ptr', Real, 'sub', True, False),
           ('subsub', SubSub, 'sub_ptr', True, True)]),
    (SubSub, [('sub_ptr', Sub, 'subsub', True, False)]),
    (OneToOne, [('onetoone', OneToOne, 's', False, True),
                ('r', Real, 'onetoone', False, False),
                ('s', OneToOne, 'onetoone', False, False)]),
    (ManyToMany, [('m', Real, 'manytomany', False, False),
                  ('s', ManyToMany, 's_rel_+', False, False)]),
    (Foreign, [('f', Real, 'foreign', False, False)]),

    (a3.Article, [('bookreview', a3.BookReview, 'article_ptr', False, True)]),
    (a3.Book, [('bookreview', a3.BookReview, 'book_ptr', True, True)]),
    (a3.BookReview, [('article_ptr', a3.Article, 'bookreview', False, False),
                     ('book_ptr', a3.Book, 'bookreview', True, False)]),

    (Piece, [('article', Article, 'piece_ptr', True, True),
             ('book', Book, 'piece_ptr', True, True)]),
    (Article, [('bookreview', BookReview, 'article_ptr', False, True),
               ('piece_ptr', Piece, 'article', True, False)]),
    (Book, [('bookreview', BookReview, 'book_ptr', True, True),
            ('piece_ptr', Piece, 'book', True, False)]),
    (BookReview, [('article_ptr', Article, 'bookreview', False, False),
                  ('book_ptr', Book, 'bookreview', True, False)]),
)
INFO_IDS = list(map(lambda i: model_label(i[0]), INFOS))


@pytest.mark.parametrize(('model', 'infos'), INFOS, ids=INFO_IDS)
def test_get_own_related_infos(model, infos):
    actual = get_own_related_infos(model)
    assert actual == infos


DIVIDE_RESULTS = (
    (A, A, ''), ('a1.a', A, ''), ('a', A, ''),
    ('a1.a.foo.bar', A, 'foo.bar'), ('a.foo.bar', A, 'foo.bar'),
    (a3.Book, a3.Book, ''), ('a3.book', a3.Book, ''),
    ('a3.book.foo.bar', a3.Book, 'foo.bar'),
    (Book, Book, ''), ('a4.book', Book, ''),
    ('a4.book.foo.bar', Book, 'foo.bar'),
)
DIVIDE_RESULTS_IDS = list(map(lambda d: model_label(d[0]), DIVIDE_RESULTS))


@pytest.mark.parametrize(('model_def', 'model', 'rest'), DIVIDE_RESULTS,
                         ids=DIVIDE_RESULTS_IDS)
def test_divide_model_def(model_def, model, rest):
    actual = divide_model_def(model_def)
    assert actual == (model, rest)


DIVIDE_FAILS = (
    'article', 'article.foo', 'a1.foo.bar', 'a1', 'a1.foo', 'a1.foo.bar',
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
    (ALL_QS, ALL_SQL), (A, ALL_SQL), ('a1.a', ALL_SQL), ('a', ALL_SQL),
    ('a1.a.all()', ALL_SQL), ('a.all()', ALL_SQL),
    (TEST_QS, TEST_SQL), ('a1.a.filter(id=1)', TEST_SQL),
    ('a.filter(id=1)', TEST_SQL)
)


@pytest.mark.parametrize(('queryset_def', 'expected_sql'), QS_DEF_RESULTS)
def test_queryset_from_def(queryset_def, expected_sql):
    queryset = queryset_from_def(queryset_def)
    assert str(queryset.query) == expected_sql
