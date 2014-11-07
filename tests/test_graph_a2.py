import pytest

from nicedjango._compat import BytesIO
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
    # TODO: not working, all of them!
    m2m_3.s.add(m2m_2)
    # m2m_4.s.add(m2m_3)
    # m2m_4.s.add(m2m_4)


@pytest.mark.django_db
@pytest.mark.parametrize(('queries', 'extras', 'expected'), (
    (Real.objects.filter(name__in=('real_3', 'subsub_1')), 'real.sub',
     {'a2': {'real': [{'id': 3, 'name': 'real_3'},
                      {'id': 6, 'name': 'subsub_1'}],
             'sub': [{'real_ptr_id': 6, 'id': 6, 'name': 'subsub_1'}]}}
     ),
    (Real.objects.filter(name__in=('real_3', 'subsub_1')),
     ('real.sub', 'sub.subsub'),
     {'a2': {'real': [{'id': 3, 'name': 'real_3'},
                      {'id': 6, 'name': 'subsub_1'}],
             'sub': [{'real_ptr_id': 6, 'id': 6, 'name': 'subsub_1'}],
             'subsub': [{'sub_ptr_id': 6, 'real_ptr_id': 6, 'id': 6,
                         'name': 'subsub_1'}]}}
     ),
    (Real, None,
     {'a2': {'real': [{'id': 1, 'name': 'real_1'},
                      {'id': 2, 'name': 'real_2'},
                      {'id': 3, 'name': 'real_3'},
                      {'id': 4, 'name': 'proxy_1'},
                      {'id': 5, 'name': 'sub_1'},
                      {'id': 6, 'name': 'subsub_1'}]}}
     ),
    (Proxy, None,
     {'a2': {'real': [{'id': 1, 'name': 'real_1'},
                      {'id': 2, 'name': 'real_2'},
                      {'id': 3, 'name': 'real_3'},
                      {'id': 4, 'name': 'proxy_1'},
                      {'id': 5, 'name': 'sub_1'},
                      {'id': 6, 'name': 'subsub_1'}]}}
     ),
    (Foreign, None,
     {'a2': {'real': [{'id': 1, 'name': 'real_1'},
                      {'id': 5, 'name': 'sub_1'}],
             'foreign': [{'f_id': None, 'id': 1, 'name': 'foreign_1'},
                         {'f_id': 1, 'id': 2, 'name': 'foreign_2'},
                         {'f_id': 1, 'id': 3, 'name': 'foreign_3'},
                         {'f_id': 5, 'id': 4, 'name': 'foreign_4'}]}}
     ),
    (Foreign, 'real.sub',
     {'a2': {'real': [{'id': 1, 'name': 'real_1'},
                      {'id': 5, 'name': 'sub_1'}],
             'foreign': [{'f_id': None, 'id': 1, 'name': 'foreign_1'},
                         {'f_id': 1, 'id': 2, 'name': 'foreign_2'},
                         {'f_id': 1, 'id': 3, 'name': 'foreign_3'},
                         {'f_id': 5, 'id': 4, 'name': 'foreign_4'}],
             'sub': [{'real_ptr_id': 5, 'id': 5, 'name': 'sub_1'}]}}
     ),
    (Sub, 'real.foreign',
     {'a2': {'real': [{'id': 5, 'name': 'sub_1'},
                      {'id': 6, 'name': 'subsub_1'}],
             'sub': [{'real_ptr_id': 5, 'id': 5, 'name': 'sub_1'},
                     {'real_ptr_id': 6, 'id': 6, 'name': 'subsub_1'}]}}
     ),
    ((Real, Sub, SubSub), None,
     {'a2': {'real': [{'id': 1, 'name': 'real_1'},
                      {'id': 2, 'name': 'real_2'},
                      {'id': 3, 'name': 'real_3'},
                      {'id': 4, 'name': 'proxy_1'},
                      {'id': 5, 'name': 'sub_1'},
                      {'id': 6, 'name': 'subsub_1'}],
             'sub': [{'real_ptr_id': 5, 'id': 5, 'name': 'sub_1'},
                     {'real_ptr_id': 6, 'id': 6, 'name': 'subsub_1'}],
             'subsub': [{'sub_ptr_id': 6, 'real_ptr_id': 6, 'id': 6,
                         'name': 'subsub_1'}]}}
     ),
    (OneToOne, None,
     {'a2': {'real': [{'id': 1, 'name': 'real_1'},
                      {'id': 2, 'name': 'real_2'},
                      {'id': 3, 'name': 'real_3'}],
             'onetoone': [{'s_id': None, 'id': 1, 'r_id': None,
                           'name': 'o2o_1'},
                          {'s_id': None, 'id': 2, 'r_id': 1, 'name': 'o2o_2'},
                          {'s_id': 1, 'id': 3, 'r_id': 2, 'name': 'o2o_3'},
                          {'s_id': 3, 'id': 4, 'r_id': 3, 'name': 'o2o_4'},
                          {'s_id': 5, 'id': 5, 'r_id': None,
                           'name': 'o2o_5'}]}}
     ),
    (OneToOne.objects.filter(name='o2o_4'), None,
     {'a2': {'real': [{'id': 2, 'name': 'real_2'},
                      {'id': 3, 'name': 'real_3'}],
             'onetoone': [{'s_id': None, 'id': 1, 'r_id': None,
                           'name': 'o2o_1'},
                          {'s_id': 1, 'id': 3, 'r_id': 2, 'name': 'o2o_3'},
                          {'s_id': 3, 'id': 4, 'r_id': 3, 'name': 'o2o_4'}]}}

     ),
    (ManyToMany, None,
     {'a2': {'real': [{u'id': 1, 'name': u'real_1'}],
             'manytomany': [{u'id': 1, 'name': u'm2m_1'},
                            {u'id': 2, 'name': u'm2m_2'},
                            {u'id': 3, 'name': u'm2m_3'},
                            {u'id': 4, 'name': u'm2m_4'}]}}
     )))
def test_dump_and_load(queries, extras, expected):
    reset_samples()
    graph = ModelGraph(queries, extras)

    stream = BytesIO()
    graph.dump_objects(stream)
    bytes_ = stream.getvalue()
    stream.close()

    delete_all()
    graph.load_objects(bytes_)
    actual = get_all_values()
    assert actual == expected
