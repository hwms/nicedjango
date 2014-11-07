from textwrap import dedent

import pytest

from nicedjango.graph import ModelGraph
from tests.a1.models import A, B, C
from tests.a2.models import Real
from tests.a3 import models as a3
from tests.a4.models import Article, Book, BookReview, Piece

TEST_DATA = [
    ('a', None, dedent("""\
       a1.a:
         ignored subs:
           a1.a.b > a1.b""")),
    ('a', 'a.b', dedent("""\
        a1.a:
          subs:
            a1.a.b > a1.b
        a1.b:
          parents:
            a1.b.a_ptr > a1.a
          ignored subs:
            a1.b.c > a1.c""")),
    ((A, B, C), None, dedent("""\
       a1.a:
         ignored subs:
           a1.a.b > a1.b
       a1.b:
         parents:
           a1.b.a_ptr > a1.a
         ignored subs:
           a1.b.c > a1.c
       a1.c:
         parents:
           a1.c.b_ptr > a1.b""")),

    (Real, None, dedent("""\
       a2.real:
         ignored subs:
           a2.real.sub > a2.sub
         ignored rels:
           a2.real.foreign > a2.foreign
           a2.real.manytomany > a2.manytomany
           a2.real.onetoone > a2.onetoone""")),

    (Real, 'real.manytomany', dedent("""\
       a2.manytomany:
         depends:
           a2.manytomany.m > a2.real
           a2.manytomany.s > a2.manytomany
       a2.real:
         relates:
           a2.real.manytomany > a2.manytomany
         ignored subs:
           a2.real.sub > a2.sub
         ignored rels:
           a2.real.foreign > a2.foreign
           a2.real.onetoone > a2.onetoone""")),

    (Real, ('real.manytomany',
            'real.onetoone',
            'real.foreign',
            'real.sub',
            'sub.subsub'), dedent("""\
       a2.foreign:
         depends:
           a2.foreign.f > a2.real
       a2.manytomany:
         depends:
           a2.manytomany.m > a2.real
           a2.manytomany.s > a2.manytomany
       a2.onetoone:
         depends:
           a2.onetoone.r > a2.real
           a2.onetoone.s > a2.onetoone
         ignored rels:
           a2.onetoone.onetoone > a2.onetoone
       a2.real:
         subs:
           a2.real.sub > a2.sub
         relates:
           a2.real.foreign > a2.foreign
           a2.real.manytomany > a2.manytomany
           a2.real.onetoone > a2.onetoone
       a2.sub:
         parents:
           a2.sub.real_ptr > a2.real
         subs:
           a2.sub.subsub > a2.subsub
       a2.subsub:
         parents:
           a2.subsub.sub_ptr > a2.sub""")),

    ((a3.Article, a3.Book, a3.BookReview), None, dedent("""\
       a3.article:
         ignored rels:
           a3.article.bookreview > a3.bookreview
       a3.book:
         ignored subs:
           a3.book.bookreview > a3.bookreview
       a3.bookreview:
         parents:
           a3.bookreview.book_ptr > a3.book
         depends:
           a3.bookreview.article_ptr > a3.article""")),

    ((Piece, Article, Book, BookReview), None, dedent("""\
       a4.article:
         parents:
           a4.article.piece_ptr > a4.piece
         ignored rels:
           a4.article.bookreview > a4.bookreview
       a4.book:
         parents:
           a4.book.piece_ptr > a4.piece
         ignored subs:
           a4.book.bookreview > a4.bookreview
       a4.bookreview:
         parents:
           a4.bookreview.book_ptr > a4.book
         depends:
           a4.bookreview.article_ptr > a4.article
       a4.piece:
         ignored subs:
           a4.piece.article > a4.article
           a4.piece.book > a4.book""")),
]
TEST_IDS = list(map(lambda d: d[:2], TEST_DATA))


@pytest.mark.parametrize(('queries', 'extras', 'expected'),
                         TEST_DATA, ids=TEST_IDS)
def test_connections_by_string(queries, extras, expected):
    graph = ModelGraph(queries, extras)
    actual = graph.as_string()
    assert actual == expected
