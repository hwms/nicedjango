from textwrap import dedent

import pytest

from nicedjango.utils import (divide_model_def, get_own_related_infos,
                              model_label, queryset_from_def)
from tests.a1.models import A, B, C
from tests.a2.models import (Abstract, Foreign, ManyToMany, OneToOne, Proxy,
                             Real, Sub, SubSub)
from tests.a3 import models as a3
from tests.a4.models import Article, Book, BookReview, Piece

INFOS = [
    (A, """\
        Field               b is par by            B.          a_ptr.
        """),
    (B, """\
        Field           a_ptr is sub by            A.             id.
        Field               c is par by            C.          b_ptr.
        """),
    (C, """\
        Field           b_ptr is sub by            B.          a_ptr.
        """),
    (Abstract, ""),
    (Real, """\
        Field         foreign is rel of      Foreign.              f.
        Field      manytomany is rel of ManyToMany_m.           real.
        Field        onetoone is rel of     OneToOne.              r.
        Field             sub is par by          Sub.       real_ptr.
        """),
    (Proxy, ""),
    (Sub, """\
        Field        real_ptr is sub by         Real.             id.
        Field          subsub is par by       SubSub.        sub_ptr.
        """),
    (SubSub, """\
        Field         sub_ptr is sub by          Sub.       real_ptr.
        """),
    (OneToOne, """\
        Field        onetoone is rel of     OneToOne.              s.
        Field               r is dep to         Real.             id.
        Field               s is dep to     OneToOne.             id.
        """),
    (ManyToMany, """\
        Field               m is rel of ManyToMany_m.           real.
        Field               s is rel of ManyToMany_s.  to_manytomany.
        """),
    (getattr(ManyToMany.m, 'through'),
     """\
        Field      manytomany is dep to   ManyToMany.             id.
        Field            real is dep to         Real.             id.
        """),
    (getattr(ManyToMany.s, 'through'),
     """\
        Field from_manytomany is dep to   ManyToMany.             id.
        Field   to_manytomany is dep to   ManyToMany.             id.
        """),
    (Foreign, """\
        Field               f is dep to         Real.             id.
        """),
    (a3.Article, """\
        Field      bookreview is rel of   BookReview.    article_ptr.
        """),
    (a3.Book, """\
        Field      bookreview is par by   BookReview.       book_ptr.
        """),
    (a3.BookReview, """\
        Field     article_ptr is dep to      Article.     article_id.
        Field        book_ptr is sub by         Book.        book_id.
        """),
    (Piece, """\
        Field         article is par by      Article.      piece_ptr.
        Field            book is par by         Book.      piece_ptr.
        """),
    (Article, """\
        Field      bookreview is rel of   BookReview.    article_ptr.
        Field       piece_ptr is sub by        Piece.             id.
        """),
    (Book, """\
        Field      bookreview is par by   BookReview.       book_ptr.
        Field       piece_ptr is sub by        Piece.             id.
        """),
    (BookReview, """\
        Field     article_ptr is dep to      Article.      piece_ptr.
        Field        book_ptr is sub by         Book.      piece_ptr.
        """),
]
INFO_IDS = list(map(lambda i: model_label(i[0]), INFOS))


@pytest.mark.parametrize(('model', 'expected'), INFOS, ids=INFO_IDS)
def test_get_own_related_infos(model, expected):
    infos = get_own_related_infos(model)
    actual_infos = ''
    for name, (rel_model, rel_field, is_dep, is_rel_pk) in infos.items():
        rel_text = {(True, True): 'sub by',
                    (True, False): 'dep to',
                    (False, True): 'par by',
                    (False, False): 'rel of'}[(is_dep, is_rel_pk)]
        actual_infos += "Field %15s is %5s %12s.%15s.\n" % (name, rel_text,
                                                            rel_model.__name__,
                                                            rel_field)
    expected = dedent(expected)
    assert actual_infos == expected


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
