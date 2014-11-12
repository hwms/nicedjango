from textwrap import dedent

import pytest
from django.utils import six

from nicedjango.graph import ModelGraph
from tests.a2.models import (Foreign, ManyToMany, OneToOne, Proxy, Real, Sub,
                             SubSub)
from tests.utils import delete_all, get_all_values


def reset_samples():
    delete_all()
    real_1 = Real.objects.create(name='real_1')
    real_2 = Real.objects.create(name='real_2')
    real_3 = Real.objects.create(name='real_3')
    Proxy.objects.create(name='proxy_1')
    sub_1 = Sub.objects.create(name='sub_1')
    SubSub.objects.create(name='subsub_1')

    Foreign.objects.create(name='foreign_1')
    Foreign.objects.create(f=real_1, name='foreign_2')
    Foreign.objects.create(f=real_1, name='foreign_3')
    Foreign.objects.create(f=sub_1, name='foreign_4')

    o2o_1 = OneToOne.objects.create(name='o2o_1')
    OneToOne.objects.create(r=real_1, name='o2o_2')
    o2o_3 = OneToOne.objects.create(r=real_2, s=o2o_1, name='o2o_3')
    OneToOne.objects.create(r=real_3, s=o2o_3, name='o2o_4')
    o2o_5 = OneToOne.objects.create(name='o2o_5')
    o2o_5.s = o2o_5
    o2o_5.save()

    ManyToMany.objects.create(name='m2m_1')
    m2m_2 = ManyToMany.objects.create(name='m2m_2')
    m2m_2.m.add(real_1)
    m2m_3 = ManyToMany.objects.create(name='m2m_3')
    m2m_4 = ManyToMany.objects.create(name='m2m_4')
    m2m_4.m.add(real_1)
    m2m_3.s.add(m2m_2)
    m2m_4.s.add(m2m_3)
    m2m_5 = ManyToMany.objects.create(name='m2m_5')
    m2m_5.s.add(m2m_3)
    m2m_5.s.add(m2m_4)
    m2m_5.s.add(m2m_5)

EXPECTED_REAL = [
    {'id': 1, 'name': 'real_1'},
    {'id': 2, 'name': 'real_2'},
    {'id': 3, 'name': 'real_3'},
    {'id': 4, 'name': 'proxy_1'},
    {'id': 5, 'name': 'sub_1'},
    {'id': 6, 'name': 'subsub_1'},
]
EXPECTED_FOREIGN_REAL = [
    {'id': 1, 'name': 'real_1'},
    {'id': 5, 'name': 'sub_1'},
]
EXPECTED_FOREIGN = [
    {'f_id': None, 'id': 1, 'name': 'foreign_1'},
    {'f_id': 1, 'id': 2, 'name': 'foreign_2'},
    {'f_id': 1, 'id': 3, 'name': 'foreign_3'},
    {'f_id': 5, 'id': 4, 'name': 'foreign_4'},
]
EXPECTED_SUB_REAL = [
    {'id': 5, 'name': 'sub_1'},
    {'id': 6, 'name': 'subsub_1'},
]
EXPECTED_SUB = [
    {'real_ptr_id': 5, 'id': 5, 'name': 'sub_1'},
    {'real_ptr_id': 6, 'id': 6, 'name': 'subsub_1'},
]
EXPECTED_SUBSUB = [
    {'id': 6, 'name': 'subsub_1', 'real_ptr_id': 6, 'sub_ptr_id': 6}
]
EXPECTED_O2O = [
    {'id': 1, 'name': 'o2o_1', 'r_id': None, 's_id': None},
    {'id': 2, 'name': 'o2o_2', 'r_id': 1, 's_id': None},
    {'id': 3, 'name': 'o2o_3', 'r_id': 2, 's_id': 1},
    {'id': 4, 'name': 'o2o_4', 'r_id': 3, 's_id': 3},
    {'id': 5, 'name': 'o2o_5', 'r_id': None, 's_id': 5}
]
EXPECTED_M2M = [
    {'id': 1, 'name': 'm2m_1'},
    {'id': 2, 'name': 'm2m_2'},
    {'id': 3, 'name': 'm2m_3'},
    {'id': 4, 'name': 'm2m_4'},
    {'id': 5, 'name': 'm2m_5'},
]
EXPECTED_M2M_S = [
    {'from_manytomany_id': 3, 'id': 1, 'to_manytomany_id': 2},
    {'from_manytomany_id': 2, 'id': 2, 'to_manytomany_id': 3},
    {'from_manytomany_id': 4, 'id': 3, 'to_manytomany_id': 3},
    {'from_manytomany_id': 3, 'id': 4, 'to_manytomany_id': 4},
    {'from_manytomany_id': 5, 'id': 5, 'to_manytomany_id': 3},
    {'from_manytomany_id': 3, 'id': 6, 'to_manytomany_id': 5},
    {'from_manytomany_id': 5, 'id': 7, 'to_manytomany_id': 4},
    {'from_manytomany_id': 4, 'id': 8, 'to_manytomany_id': 5},
    {'from_manytomany_id': 5, 'id': 9, 'to_manytomany_id': 5}
]
EXPECTED_M2M_M = [
    {'real_id': 1, 'manytomany_id': 2, 'id': 1},
    {'real_id': 1, 'manytomany_id': 4, 'id': 2},
]
EXPECTED_M2M_M_M2M = [
    {'id': 2, 'name': 'm2m_2'},
    {'id': 4, 'name': 'm2m_4'},
]
EXPECTED_M2M_REAL = [
    {'id': 1, 'name': 'real_1'},
]


@pytest.mark.django_db
def test_original_values():
    reset_samples()
    expected = {'a2.foreign': EXPECTED_FOREIGN,
                'a2.manytomany': EXPECTED_M2M,
                'a2.manytomany_m': EXPECTED_M2M_M,
                'a2.manytomany_s': EXPECTED_M2M_S,
                'a2.onetoone': EXPECTED_O2O,
                'a2.real': EXPECTED_REAL,
                'a2.sub': EXPECTED_SUB,
                'a2.subsub': EXPECTED_SUBSUB}
    actual = get_all_values()
    assert actual == expected


@pytest.mark.django_db
def test_dump_and_load_all():
    reset_samples()
    expected = get_all_values()
    graph = ModelGraph(app='a2')

    stream = six.StringIO()
    graph.dump_objects(stream)
    value = stream.getvalue()
    stream.close()

    delete_all()
    graph.load_objects(value)
    actual = get_all_values()
    assert actual == expected


@pytest.mark.django_db
@pytest.mark.parametrize(('queries', 'extras', 'expected_dump', 'expected'), (
    (Real.objects.filter(name__in=('real_3', 'subsub_1')), 'real.sub', """\
        ---
        - a2.real: [id, name]
        - [3, real_3]
        - [6, subsub_1]
        ---
        - a2.sub: [real_ptr]
        - [6]
        """,
        {'a2.real':
            [{'id': 3, 'name': 'real_3'},
             {'id': 6, 'name': 'subsub_1'}],
         'a2.sub':
            [{'real_ptr_id': 6, 'id': 6, 'name': 'subsub_1'}],
         }),
    (Real.objects.filter(name__in=('real_3', 'subsub_1')),
        ('real.sub', 'sub.subsub'), """\
        ---
        - a2.real: [id, name]
        - [3, real_3]
        - [6, subsub_1]
        ---
        - a2.sub: [real_ptr]
        - [6]
        ---
        - a2.subsub: [sub_ptr]
        - [6]
        """,
        {'a2.real':
            [{'id': 3, 'name': 'real_3'},
             {'id': 6, 'name': 'subsub_1'}],
         'a2.sub':
            [{'real_ptr_id': 6, 'id': 6, 'name': 'subsub_1'}],
         'a2.subsub':
            [{'sub_ptr_id': 6, 'real_ptr_id': 6, 'id': 6, 'name': 'subsub_1'}],
         }),
    (Real, None, """\
        ---
        - a2.real: [id, name]
        - [1, real_1]
        - [2, real_2]
        - [3, real_3]
        - [4, proxy_1]
        - [5, sub_1]
        - [6, subsub_1]
        """,
        {'a2.real': EXPECTED_REAL}),
    (Proxy, None, """\
        ---
        - a2.proxy: [id, name]
        - [1, real_1]
        - [2, real_2]
        - [3, real_3]
        - [4, proxy_1]
        - [5, sub_1]
        - [6, subsub_1]
        """,
        {'a2.real': EXPECTED_REAL}),
    (Foreign, None, """\
        ---
        - a2.real: [id, name]
        - [1, real_1]
        - [5, sub_1]
        ---
        - a2.foreign: [id, name, f]
        - [1, foreign_1, null]
        - [2, foreign_2, 1]
        - [3, foreign_3, 1]
        - [4, foreign_4, 5]
        """,
        {'a2.real': EXPECTED_FOREIGN_REAL,
         'a2.foreign': EXPECTED_FOREIGN,
         }),
    (Foreign, 'real.sub', """\
        ---
        - a2.real: [id, name]
        - [1, real_1]
        - [5, sub_1]
        ---
        - a2.sub: [real_ptr]
        - [5]
        ---
        - a2.foreign: [id, name, f]
        - [1, foreign_1, null]
        - [2, foreign_2, 1]
        - [3, foreign_3, 1]
        - [4, foreign_4, 5]
        """,
        {'a2.real': EXPECTED_FOREIGN_REAL,
         'a2.foreign': EXPECTED_FOREIGN,
         'a2.sub':
            [{'real_ptr_id': 5, 'id': 5, 'name': 'sub_1'}],
         }),
    (Sub, None, """\
        ---
        - a2.real: [id, name]
        - [5, sub_1]
        - [6, subsub_1]
        ---
        - a2.sub: [real_ptr]
        - [5]
        - [6]
        """,
        {'a2.real': EXPECTED_SUB_REAL,
         'a2.sub': EXPECTED_SUB,
         }),
    (Sub, 'real.foreign', """\
        ---
        - a2.real: [id, name]
        - [5, sub_1]
        - [6, subsub_1]
        ---
        - a2.sub: [real_ptr]
        - [5]
        - [6]
        ---
        - a2.foreign: [id, name, f]
        - [4, foreign_4, 5]
        """,
        {'a2.real': EXPECTED_SUB_REAL,
         'a2.sub': EXPECTED_SUB,
         'a2.foreign':
            [{'f_id': 5, 'id': 4, 'name': 'foreign_4'}],
         }),
    ((Real, Sub, SubSub), None, """\
        ---
        - a2.real: [id, name]
        - [1, real_1]
        - [2, real_2]
        - [3, real_3]
        - [4, proxy_1]
        - [5, sub_1]
        - [6, subsub_1]
        ---
        - a2.sub: [real_ptr]
        - [5]
        - [6]
        ---
        - a2.subsub: [sub_ptr]
        - [6]
        """,
        {'a2.real': EXPECTED_REAL,
         'a2.sub': EXPECTED_SUB,
         'a2.subsub': EXPECTED_SUBSUB,
         }),
    (OneToOne, None, """\
        ---
        - a2.real: [id, name]
        - [1, real_1]
        - [2, real_2]
        - [3, real_3]
        ---
        - a2.onetoone: [id, name, r, s]
        - [1, o2o_1, null, null]
        - [2, o2o_2, 1, null]
        - [3, o2o_3, 2, 1]
        - [4, o2o_4, 3, 3]
        - [5, o2o_5, null, 5]
        """,
        {'a2.real':
            [{'id': 1, 'name': 'real_1'},
             {'id': 2, 'name': 'real_2'},
             {'id': 3, 'name': 'real_3'}],
         'a2.onetoone':
            [{'s_id': None, 'id': 1, 'r_id': None, 'name': 'o2o_1'},
             {'s_id': None, 'id': 2, 'r_id': 1, 'name': 'o2o_2'},
             {'s_id': 1, 'id': 3, 'r_id': 2, 'name': 'o2o_3'},
             {'s_id': 3, 'id': 4, 'r_id': 3, 'name': 'o2o_4'},
             {'s_id': 5, 'id': 5, 'r_id': None, 'name': 'o2o_5'}],
         }),
    (OneToOne.objects.filter(name='o2o_4'), None, """\
        ---
        - a2.real: [id, name]
        - [2, real_2]
        - [3, real_3]
        ---
        - a2.onetoone: [id, name, r, s]
        - [1, o2o_1, null, null]
        - [3, o2o_3, 2, 1]
        - [4, o2o_4, 3, 3]
        """,
        {'a2.real':
            [{'id': 2, 'name': 'real_2'},
             {'id': 3, 'name': 'real_3'}],
         'a2.onetoone':
            [{'s_id': None, 'id': 1, 'r_id': None, 'name': 'o2o_1'},
             {'s_id': 1, 'id': 3, 'r_id': 2, 'name': 'o2o_3'},
             {'s_id': 3, 'id': 4, 'r_id': 3, 'name': 'o2o_4'}],
         }),
    ('manytomany_m', None, """\
        ---
        - a2.manytomany: [id, name]
        - [2, m2m_2]
        - [4, m2m_4]
        ---
        - a2.real: [id, name]
        - [1, real_1]
        ---
        - a2.manytomany_m: [id, manytomany, real]
        - [1, 2, 1]
        - [2, 4, 1]
        """,
        {'a2.manytomany_m':
            [{'real_id': 1, 'manytomany_id': 2, 'id': 1},
             {'real_id': 1, 'manytomany_id': 4, 'id': 2}],
         'a2.real':
            [{'id': 1, 'name': 'real_1'}],
         'a2.manytomany':
            [{'id': 2, 'name': 'm2m_2'},
             {'id': 4, 'name': 'm2m_4'}]
         }),
    (ManyToMany, 'manytomany.s', """\
        ---
        - a2.manytomany: [id, name]
        - [1, m2m_1]
        - [2, m2m_2]
        - [3, m2m_3]
        - [4, m2m_4]
        - [5, m2m_5]
        ---
        - a2.manytomany_s: [id, from_manytomany, to_manytomany]
        - [1, 3, 2]
        - [2, 2, 3]
        - [3, 4, 3]
        - [4, 3, 4]
        - [5, 5, 3]
        - [6, 3, 5]
        - [7, 5, 4]
        - [8, 4, 5]
        - [9, 5, 5]
        """,
        {'a2.manytomany': EXPECTED_M2M,
         'a2.manytomany_s': EXPECTED_M2M_S,
         }),
    (Real, 'real.manytomany', """\
        ---
        - a2.manytomany: [id, name]
        - [2, m2m_2]
        - [4, m2m_4]
        ---
        - a2.real: [id, name]
        - [1, real_1]
        - [2, real_2]
        - [3, real_3]
        - [4, proxy_1]
        - [5, sub_1]
        - [6, subsub_1]
        ---
        - a2.manytomany_m: [id, manytomany, real]
        - [1, 2, 1]
        - [2, 4, 1]
        """,
     {'a2.real': EXPECTED_REAL,
      'a2.manytomany_m': EXPECTED_M2M_M,
      'a2.manytomany': EXPECTED_M2M_M_M2M,
      }),
    (Real, ('real.manytomany', 'manytomany.s'), """\
        ---
        - a2.manytomany: [id, name]
        - [2, m2m_2]
        - [3, m2m_3]
        - [4, m2m_4]
        - [5, m2m_5]
        ---
        - a2.manytomany_s: [id, from_manytomany, to_manytomany]
        - [1, 3, 2]
        - [2, 2, 3]
        - [3, 4, 3]
        - [4, 3, 4]
        - [5, 5, 3]
        - [6, 3, 5]
        - [7, 5, 4]
        - [8, 4, 5]
        - [9, 5, 5]
        ---
        - a2.real: [id, name]
        - [1, real_1]
        - [2, real_2]
        - [3, real_3]
        - [4, proxy_1]
        - [5, sub_1]
        - [6, subsub_1]
        ---
        - a2.manytomany_m: [id, manytomany, real]
        - [1, 2, 1]
        - [2, 4, 1]
        """,
     {'a2.real': EXPECTED_REAL,
      'a2.manytomany_m': EXPECTED_M2M_M,
      'a2.manytomany_s': EXPECTED_M2M_S,
      'a2.manytomany': EXPECTED_M2M[1:],
      }),
))
def test_dump_and_load(queries, extras, expected_dump, expected):
    reset_samples()
    graph = ModelGraph(queries, extras)
    expected_dump = dedent(expected_dump)

    stream = six.StringIO()
    graph.dump_objects(stream)
    value = stream.getvalue()
    stream.close()

    assert value == expected_dump

    delete_all()
    graph.load_objects(value)
    actual = get_all_values()
    assert actual == expected
