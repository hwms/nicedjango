from __future__ import unicode_literals
from collections import OrderedDict

from tests.a1.models import A, B, C, D, E, F, G, M, M_d, M_s, O, P
from tests.a4.models import Question, Response, Sample
from tests.utils import delete_all


def reset_samples():
    delete_all()
    a_1 = A.objects.create(id='A1')
    A.objects.create(id='A2')

    B.objects.create(id='B1')
    c_1 = C.objects.create(id='C1')
    c_2 = C.objects.create(id='C2')
    d_1 = D.objects.create(id='D1')
    E.objects.create(id='E1')
    P.objects.create(id='P1')

    F.objects.create(id='F1')
    F.objects.create(a=a_1, id='F2')
    F.objects.create(a=a_1, id='F3')
    F.objects.create(a=d_1, id='F4')
    G.objects.create(d=d_1, id='G1')

    o_1 = O.objects.create(id='O1')
    O.objects.create(c=c_1, id='O2')
    o_3 = O.objects.create(c=c_2, s=o_1, id='O3')
    O.objects.create(c=d_1, s=o_3, id='O4')
    o_5 = O.objects.create(id='O5')
    o_5.s = o_5
    o_5.save()

    m_1 = M.objects.create(id='M1')
    m_2 = M.objects.create(id='M2')
    m_2.s.add(m_1)
    m_3 = M.objects.create(id='M3')
    m_3.d.add(d_1)
    m_4 = M.objects.create(id='M4')
    m_4.d.add(d_1)
    m_4.s.add(m_3)
    m_5 = M.objects.create(id='M5')
    m_5.s.add(m_3)
    m_5.s.add(m_4)
    m_5.s.add(m_5)

    q_1 = Question.objects.create(id='Q1', pub_date='2014-01-01', question_text='what question 1?')
    q_2 = Question.objects.create(id='Q2', pub_date='2014-01-02', question_text='what question 2?')
    q_3 = Question.objects.create(id='Q3', pub_date='2014-01-03', question_text='what question 3?')
    Response.objects.create(id='R1', question=q_1, response_text='NULL')
    Response.objects.create(id='R2', question=q_1, response_text='None', votes=111)
    Response.objects.create(id='R3', question=q_2, response_text='foo', votes=222)
    Response.objects.create(id='R4', question=q_2, response_text='bar', votes=333)
    Response.objects.create(id='R5', question=q_3, response_text='foobar', votes=444)

    Sample.objects.create(id='S1', bool=True, nullbool=False, date='2014-02-01', time='01:01',
                          dec='12.34', float=1.23, text='foobar', comma=[1, 2, 3], slug='abc')
    Sample.objects.create(id='S2', bool=False, nullbool=True, date='2014-02-02', time='01:02',
                          dec='56.78', float=3.45, text='\xc2', comma=[4, 5, 6], slug='def')
    Sample.objects.create(id='S3', bool=True, nullbool=None, date='2014-02-03', time='01:03',
                          dec='-9.12', float=6.78, text='', comma=[])


SAMPLES = OrderedDict([
    ('a', ((A,), ())),
    ('b', ((B,), ())),
    ('c', ((C,), ())),
    ('d', ((D,), ())),
    ('e', ((E,), ())),
    ('f', ((F,), ())),
    ('g', ((G,), ())),
    # TODO: ('p', ((P,), ())),
    ('o', ((O,), ())),
    ('m', ((M,), ())),
    ('m_d', ((M_d,), ())),
    ('m_s', ((M_s,), ())),
    ('a_some', ((A.objects.filter(id__in=('A2', 'D1')),), ())),
    ('a_some_a_b', ((A.objects.filter(id__in=('A2', 'D1')),), ('a.b',))),
    ('f_a_d', ((F,), ('a.d',))),
    ('d_a_f', ((D,), ('a.f',))),
    ('o_one_o_s', ((O.objects.filter(id='O4'),), (),)),
    ('m_one_m_s', ((M.objects.filter(id='M5'),), ('m.s',))),
    ('d_d_m', ((D,), ('d.m',))),
    ('d_d_m_m_s', ((D,), ('d.m', 'm.s'))),
    ('q', ((Question,), ())),
    ('q_r', ((Question,), ('question.response'))),
    ('s', ((Sample,), ())),
])
