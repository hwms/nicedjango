from textwrap import dedent

import pytest

from nicedjango.graph import ModelGraph
from nicedjango.graph.utils import nodes_as_string
from tests.a1.models import A, B, C, D
from tests.a2 import models as a2
from tests.a3.models import Article, Book, BookReview, Piece

TEST_DATA = [
    ('a', None, """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        """),
    ('a', 'a.b', """\
        a1-a:
                  a1-a.b          to child            a1-b.pk
          excludes:
                  a1-a.f          to foreign          a1-f.a
        a1-b:
                  a1-b.pk         to parent           a1-a.pk
          excludes:
                  a1-b.c          to child            a1-c.pk
                  a1-b.e          to child            a1-e.pk
        """),
    ((A, B, C), None, """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        a1-b:
                  a1-b.pk         to parent           a1-a.pk
          excludes:
                  a1-b.c          to child            a1-c.pk
                  a1-b.e          to child            a1-e.pk
        a1-c:
                  a1-c.pk         to parent           a1-b.pk
          excludes:
                  a1-c.o          to foreign          a1-o.c
                  a1-c.d          to child            a1-d.pk
        """),
    (D, None, """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        a1-b:
                  a1-b.pk         to parent           a1-a.pk
          excludes:
                  a1-b.c          to child            a1-c.pk
                  a1-b.e          to child            a1-e.pk
        a1-c:
                  a1-c.pk         to parent           a1-b.pk
          excludes:
                  a1-c.o          to foreign          a1-o.c
                  a1-c.d          to child            a1-d.pk
        a1-d:
                  a1-d.pk         to parent           a1-c.pk
          excludes:
                  a1-d.g          to foreign          a1-g.d
                  a1-d.m          to foreign        a1-m_d.d
        """),
    (D, 'd.m', """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        a1-b:
                  a1-b.pk         to parent           a1-a.pk
          excludes:
                  a1-b.c          to child            a1-c.pk
                  a1-b.e          to child            a1-e.pk
        a1-c:
                  a1-c.pk         to parent           a1-b.pk
          excludes:
                  a1-c.o          to foreign          a1-o.c
                  a1-c.d          to child            a1-d.pk
        a1-d:
                  a1-d.m          to foreign        a1-m_d.d
                  a1-d.pk         to parent           a1-c.pk
          excludes:
                  a1-d.g          to foreign          a1-g.d
        a1-m:
          excludes:
                  a1-m.d          to foreign        a1-m_d.d
                  a1-m.s          to foreign        a1-m_s.to_m
        a1-m_d:
                a1-m_d.d          to dependency       a1-d.pk
                a1-m_d.m          to dependency       a1-m.pk
        """),
    (D, ('d.m', 'd.o', 'd.f'), """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        a1-b:
                  a1-b.pk         to parent           a1-a.pk
          excludes:
                  a1-b.c          to child            a1-c.pk
                  a1-b.e          to child            a1-e.pk
        a1-c:
                  a1-c.pk         to parent           a1-b.pk
          excludes:
                  a1-c.o          to foreign          a1-o.c
                  a1-c.d          to child            a1-d.pk
        a1-d:
                  a1-d.m          to foreign        a1-m_d.d
                  a1-d.pk         to parent           a1-c.pk
          excludes:
                  a1-d.g          to foreign          a1-g.d
        a1-m:
          excludes:
                  a1-m.d          to foreign        a1-m_d.d
                  a1-m.s          to foreign        a1-m_s.to_m
        a1-m_d:
                a1-m_d.d          to dependency       a1-d.pk
                a1-m_d.m          to dependency       a1-m.pk
       """),
    ((a2.Article, a2.Book, a2.BookReview), None, """\
        a2-article:
          excludes:
            a2-article.bookreview to foreign    a2-bookreview.article_ptr
        a2-book:
          excludes:
               a2-book.bookreview to child      a2-bookreview.pk
        a2-bookreview:
            a2-bookreview.article_ptr to dependency a2-article.pk
            a2-bookreview.pk         to parent        a2-book.pk
       """),
    ((Piece, Article, Book, BookReview), None, """\
        a3-piece:
          excludes:
              a3-piece.article    to child      a3-article.pk
              a3-piece.book       to child         a3-book.pk
        a3-article:
            a3-article.pk         to parent       a3-piece.pk
          excludes:
            a3-article.bookreview to foreign    a3-bookreview.article_ptr
        a3-book:
               a3-book.pk         to parent       a3-piece.pk
          excludes:
               a3-book.bookreview to child      a3-bookreview.pk
        a3-bookreview:
            a3-bookreview.article_ptr to dependency a3-article.pk
            a3-bookreview.pk         to parent        a3-book.pk
       """),
]
TEST_IDS = list(map(lambda d: d[:2], TEST_DATA))


@pytest.mark.parametrize(('queries', 'relations', 'expected'),
                         TEST_DATA, ids=TEST_IDS)
def test_connections_by_string(queries, relations, expected):
    graph = ModelGraph(queries, relations)
    actual = nodes_as_string(graph.nodes.values()) + '\n'
    expected = dedent(expected)
    # print '*******'
    # print queries, relations
    # print actual
    # print '*******'
    assert actual == expected
