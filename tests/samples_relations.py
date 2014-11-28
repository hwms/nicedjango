SAMPLES_RELATIONS = {
    'a': """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        """,
    'b': """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        a1-b:
                  a1-b.pk         to parent           a1-a.pk
          excludes:
                  a1-b.c          to child            a1-c.pk
                  a1-b.e          to child            a1-e.pk
        """,
    'c': """\
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
        """,
    'd': """\
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
        """,
    'e': """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        a1-b:
                  a1-b.pk         to parent           a1-a.pk
          excludes:
                  a1-b.c          to child            a1-c.pk
                  a1-b.e          to child            a1-e.pk
        a1-e:
                  a1-e.pk         to parent           a1-b.pk
        """,
    'f': """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        a1-f:
                  a1-f.a          to dependency       a1-a.pk
        """,
    'g': """\
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
        a1-g:
                  a1-g.d          to dependency       a1-d.pk
        """,
    'o': """\
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
        a1-o:
                  a1-o.c          to dependency       a1-c.pk
                  a1-o.s          to self             a1-o.pk
          excludes:
                  a1-o.o          to self             a1-o.s
        """,
    'm': """\
        a1-m:
          excludes:
                  a1-m.d          to foreign        a1-m_d.d
                  a1-m.s          to foreign        a1-m_s.to_m
        """,
    'm_d': """\
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
        a1-m:
          excludes:
                  a1-m.d          to foreign        a1-m_d.d
                  a1-m.s          to foreign        a1-m_s.to_m
        a1-m_d:
                a1-m_d.d          to dependency       a1-d.pk
                a1-m_d.m          to dependency       a1-m.pk
        """,
    'm_s': """\
        a1-m:
          excludes:
                  a1-m.d          to foreign        a1-m_d.d
                  a1-m.s          to foreign        a1-m_s.to_m
        a1-m_s:
                a1-m_s.from_m     to dependency       a1-m.pk
                a1-m_s.to_m       to dependency       a1-m.pk
        """,
    'a_some': """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        """,
    'a_some_a_b': """\
        a1-a:
                  a1-a.b          to child            a1-b.pk
          excludes:
                  a1-a.f          to foreign          a1-f.a
        a1-b:
                  a1-b.pk         to parent           a1-a.pk
          excludes:
                  a1-b.c          to child            a1-c.pk
                  a1-b.e          to child            a1-e.pk
        """,
    'f_a_d': """\
        a1-a:
          excludes:
                  a1-a.f          to foreign          a1-f.a
                  a1-a.b          to child            a1-b.pk
        a1-f:
                  a1-f.a          to dependency       a1-a.pk
        """,
    'd_a_f': """\
        a1-a:
                  a1-a.f          to foreign          a1-f.a
          excludes:
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
        a1-f:
                  a1-f.a          to dependency       a1-a.pk
        """,
    'o_one_o_s': """\
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
        a1-o:
                  a1-o.c          to dependency       a1-c.pk
                  a1-o.s          to self             a1-o.pk
          excludes:
                  a1-o.o          to self             a1-o.s
        """,
    'm_one_m_s': """\
        a1-m:
                  a1-m.s          to foreign        a1-m_s.to_m
          excludes:
                  a1-m.d          to foreign        a1-m_d.d
        a1-m_s:
                a1-m_s.from_m     to dependency       a1-m.pk
                a1-m_s.to_m       to dependency       a1-m.pk
        """,
    'd_d_m': """\
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
        """,
    'd_d_m_m_s': """\
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
                  a1-m.s          to foreign        a1-m_s.to_m
          excludes:
                  a1-m.d          to foreign        a1-m_d.d
        a1-m_d:
                a1-m_d.d          to dependency       a1-d.pk
                a1-m_d.m          to dependency       a1-m.pk
        a1-m_s:
                a1-m_s.from_m     to dependency       a1-m.pk
                a1-m_s.to_m       to dependency       a1-m.pk
        """,
    'q': """\
        a4-question:
          excludes:
            a4-question.response   to foreign    a4-response.question
        """,
    'q_r': """\
        a4-question:
            a4-question.response   to foreign    a4-response.question
        a4-response:
            a4-response.question   to dependency a4-question.pk
        """,
    'a2': """\
        a2-article:
          excludes:
            a2-article.bookreview to foreign    a2-bookreview.article_ptr
        a2-book:
          excludes:
               a2-book.bookreview to child      a2-bookreview.pk
        a2-bookreview:
            a2-bookreview.article_ptr to dependency a2-article.pk
            a2-bookreview.pk         to parent        a2-book.pk
        """,
    'a3': """\
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
        """,
}
