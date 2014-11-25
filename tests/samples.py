from collections import OrderedDict

from tests.a1.models import A, B, C, D, E, F, G, M, M_d, M_s, O, P
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
])
