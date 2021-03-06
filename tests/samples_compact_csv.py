from __future__ import unicode_literals


SAMPLES_CSV = {
    'a': """\
        a1-a
            a1-a:pk
            "A1"
            "A2"
            "B1"
            "C1"
            "C2"
            "D1"
            "E1"
            "P1"
        """,
    'b': """\
        a1-a
            a1-a:pk
            "B1"
            "C1"
            "C2"
            "D1"
            "E1"
        a1-b
            a1-b:pk
            "B1"
            "C1"
            "C2"
            "D1"
            "E1"
        """,
    'c': """\
        a1-a
            a1-a:pk
            "C1"
            "C2"
            "D1"
        a1-b
            a1-b:pk
            "C1"
            "C2"
            "D1"
        a1-c
            a1-c:pk
            "C1"
            "C2"
            "D1"
        """,
    'd': """\
        a1-a
            a1-a:pk
            "D1"
        a1-b
            a1-b:pk
            "D1"
        a1-c
            a1-c:pk
            "D1"
        a1-d
            a1-d:pk
            "D1"
        """,
    'e': """\
        a1-a
            a1-a:pk
            "E1"
        a1-b
            a1-b:pk
            "E1"
        a1-e
            a1-e:pk
            "E1"
                """,
    'f': """\
        a1-a
            a1-a:pk
            "A1"
            "D1"
        a1-f
            a1-f:pk,a
            "F1",NULL
            "F2","A1"
            "F3","A1"
            "F4","D1"
        """,
    'g': """\
        a1-a
            a1-a:pk
            "D1"
        a1-b
            a1-b:pk
            "D1"
        a1-c
            a1-c:pk
            "D1"
        a1-d
            a1-d:pk
            "D1"
        a1-g
            a1-g:pk,d
            "G1","D1"
                """,
    'p': """\
        a1-p
            a1-a:pk
            "A1"
            "A2"
            "B1"
            "C1"
            "C2"
            "D1"
            "E1"
            "P1"
        """,
    'o': """\
        a1-a
            a1-a:pk
            "C1"
            "C2"
            "D1"
        a1-b
            a1-b:pk
            "C1"
            "C2"
            "D1"
        a1-c
            a1-c:pk
            "C1"
            "C2"
            "D1"
        a1-o
            a1-o:pk,c,s
            "O1",NULL,NULL
            "O2","C1",NULL
            "O3","C2","O1"
            "O4","D1","O3"
            "O5",NULL,"O5"
        """,
    'm': """\
        a1-m
            a1-m:pk
            "M1"
            "M2"
            "M3"
            "M4"
            "M5"
        """,
    'm_d': """\
        a1-a
            a1-a:pk
            "D1"
        a1-b
            a1-b:pk
            "D1"
        a1-c
            a1-c:pk
            "D1"
        a1-d
            a1-d:pk
            "D1"
        a1-m
            a1-m:pk
            "M3"
            "M4"
        a1-m_d
            a1-m_d:pk,d,m
            1,"D1","M3"
            2,"D1","M4"
        """,
    'm_s': """\
        a1-m
            a1-m:pk
            "M1"
            "M2"
            "M3"
            "M4"
            "M5"
        a1-m_s
            a1-m_s:pk,from_m,to_m
            1,"M2","M1"
            2,"M1","M2"
            3,"M4","M3"
            4,"M3","M4"
            5,"M5","M3"
            6,"M3","M5"
            7,"M5","M4"
            8,"M4","M5"
            9,"M5","M5"
        """,
    'a_some': """\
        a1-a
            a1-a:pk
            "A2"
            "D1"
        """,
    'a_some_a_b': """\
        a1-a
            a1-a:pk
            "A2"
            "D1"
        a1-b
            a1-b:pk
            "D1"
        """,
    'f_a_d': """\
        a1-a
            a1-a:pk
            "A1"
            "D1"
        a1-f
            a1-f:pk,a
            "F1",NULL
            "F2","A1"
            "F3","A1"
            "F4","D1"
        """,
    'd_a_f': """\
        a1-a
            a1-a:pk
            "D1"
        a1-b
            a1-b:pk
            "D1"
        a1-c
            a1-c:pk
            "D1"
        a1-d
            a1-d:pk
            "D1"
        a1-f
            a1-f:pk,a
            "F4","D1"
        """,
    'o_one_o_s': """\
        a1-a
            a1-a:pk
            "C2"
            "D1"
        a1-b
            a1-b:pk
            "C2"
            "D1"
        a1-c
            a1-c:pk
            "C2"
            "D1"
        a1-o
            a1-o:pk,c,s
            "O1",NULL,NULL
            "O3","C2","O1"
            "O4","D1","O3"
        """,
    'm_one_m_s': """\
        a1-m
            a1-m:pk
            "M3"
            "M4"
            "M5"
        a1-m_s
            a1-m_s:pk,from_m,to_m
            3,"M4","M3"
            4,"M3","M4"
            5,"M5","M3"
            6,"M3","M5"
            7,"M5","M4"
            8,"M4","M5"
            9,"M5","M5"
        """,
    'd_d_m': """\
        a1-a
            a1-a:pk
            "D1"
        a1-b
            a1-b:pk
            "D1"
        a1-c
            a1-c:pk
            "D1"
        a1-d
            a1-d:pk
            "D1"
        a1-m
            a1-m:pk
            "M3"
            "M4"
        a1-m_d
            a1-m_d:pk,d,m
            1,"D1","M3"
            2,"D1","M4"
        """,
    'd_d_m_m_s': """\
        a1-a
            a1-a:pk
            "D1"
        a1-b
            a1-b:pk
            "D1"
        a1-c
            a1-c:pk
            "D1"
        a1-d
            a1-d:pk
            "D1"
        a1-m
            a1-m:pk
            "M3"
            "M4"
            "M5"
        a1-m_d
            a1-m_d:pk,d,m
            1,"D1","M3"
            2,"D1","M4"
        a1-m_s
            a1-m_s:pk,from_m,to_m
            3,"M4","M3"
            4,"M3","M4"
            5,"M5","M3"
            6,"M3","M5"
            7,"M5","M4"
            8,"M4","M5"
            9,"M5","M5"
        """,
    'a2': """\
        a2-article
            a2-article:pk,headline
            1,"The only Review for The explicit AutoField"
        a2-book
            a2-book:pk,title
            1,"The explicit AutoField"
        a2-bookreview
            a2-bookreview:pk,article_ptr
            1,1
        """,
    'a3': """\
        a3-piece
            a3-piece:pk
            1
        a3-article
            a3-article:pk,headline
            1,"The only Review for The common ancestor"
        a3-book
            a3-book:pk,title
            1,"The common ancestor"
        a3-bookreview
            a3-bookreview:pk,article_ptr
            1,1
        """,
    'q': """\
        a4-question
            a4-question:pk,pub_date,question_text
            "Q1",2014-01-01 00:00:00,"what question 1?"
            "Q2",2014-01-02 00:00:00,"what question 2?"
            "Q3",2014-01-03 00:00:00,"what question 3?"
        """,
    'q_r': """\
        a4-question
            a4-question:pk,pub_date,question_text
            "Q1",2014-01-01 00:00:00,"what question 1?"
            "Q2",2014-01-02 00:00:00,"what question 2?"
            "Q3",2014-01-03 00:00:00,"what question 3?"
        a4-response
            a4-response:pk,question,response_text,votes
            "R1","Q1","NULL",0
            "R2","Q1","None",111
            "R3","Q2","foo",222
            "R4","Q2","bar",333
            "R5","Q3","foobar",444
        """,
    's': """\
        a4-sample
            a4-sample:pk,bool,comma,date,dec,float,nullbool,slug,text,time
            "S1",1,"[1, 2, 3]",2014-02-01,12.34,1.23,0,"abc","foobar",01:01:00
            "S2",0,"[4, 5, 6]",2014-02-02,56.78,3.45,1,"def","\xc2",01:02:00
            "S3",1,"[]",2014-02-03,-9.12,6.78,NULL,"","",01:03:00
        """,
}
