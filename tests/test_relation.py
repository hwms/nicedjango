from textwrap import dedent

import pytest

from nicedjango.graph.graph import ModelGraph
from nicedjango.graph.relation import get_relations
from nicedjango.utils import model_label
from tests.a1.models import A, B, C, D, E, F, G, M, M_d, M_s, Model, O, P
from tests.a2 import models as a2
from tests.a3.models import Article, Book, BookReview, Piece

RELATIONS = [
    (Model, ""),
    (A, """\
        a1-a.b          to child            a1-b.pk
        a1-a.f          to foreign          a1-f.a
        """),
    (B, """\
        a1-b.pk         to parent           a1-a.pk
        a1-b.c          to child            a1-c.pk
        a1-b.e          to child            a1-e.pk
        """),
    (C, """\
        a1-c.pk         to parent           a1-b.pk
        a1-c.d          to child            a1-d.pk
        a1-c.o          to foreign          a1-o.c
        """),
    (D, """\
        a1-d.pk         to parent           a1-c.pk
        a1-d.g          to foreign          a1-g.d
        a1-d.m          to foreign        a1-m_d.d
        """),
    (E, """\
        a1-e.pk         to parent           a1-b.pk
        """,),
    (F, """\
        a1-f.a          to dependency       a1-a.pk
        """),
    (G, """\
        a1-g.d          to dependency       a1-d.pk
        """),
    (P, ""),
    (O, """\
        a1-o.c          to dependency       a1-c.pk
        a1-o.o          to self             a1-o.s
        a1-o.s          to self             a1-o.pk
        """),
    (M, """\
        a1-m.d          to foreign        a1-m_d.d
        a1-m.s          to foreign        a1-m_s.to_m
        """),
    (M_d, """\
        a1-m_d.d          to dependency       a1-d.pk
        a1-m_d.m          to dependency       a1-m.pk
        """),
    (M_s, """\
        a1-m_s.from_m     to dependency       a1-m.pk
        a1-m_s.to_m       to dependency       a1-m.pk
        """),
    (a2.Article, """\
        a2-article.bookreview to foreign    a2-bookreview.article_ptr
        """),
    (a2.Book, """\
        a2-book.bookreview to child      a2-bookreview.pk
        """),
    (a2.BookReview, """\
        a2-bookreview.article_ptr to dependency a2-article.pk
        a2-bookreview.pk         to parent        a2-book.pk
        """),
    (Piece, """\
        a3-piece.article    to child      a3-article.pk
        a3-piece.book       to child         a3-book.pk
        """),
    (Article, """\
        a3-article.bookreview to foreign    a3-bookreview.article_ptr
        a3-article.pk         to parent       a3-piece.pk
        """),
    (Book, """\
        a3-book.bookreview to child      a3-bookreview.pk
        a3-book.pk         to parent       a3-piece.pk
        """),
    (BookReview, """\
        a3-bookreview.article_ptr to dependency a3-article.pk
        a3-bookreview.pk         to parent        a3-book.pk
        """),
]
RELATION_IDS = list(map(lambda i: model_label(i[0]), RELATIONS))


@pytest.mark.parametrize(('model', 'expected'), RELATIONS, ids=RELATION_IDS)
def test_get_relations(model, expected):
    expected = dedent(expected)[:-1]
    graph = ModelGraph()
    rels = get_relations(graph.get_node(model)).values()
    actual = '\n'.join(map(str, rels))
    # print '******'
    # print model
    # print actual
    # print '******'
    assert dedent(actual) == expected
