import os
import tempfile
from collections import defaultdict

import pytest
from django.core.management import call_command

from nicedjango.graph import ModelGraph
from nicedjango.utils import model_label
from tests.testapp.models import (Foreign, ManyToMany, OneToOne, Proxy, Real,
                                  Sub, SubSub)

MODELS = [Real, Proxy, Sub, SubSub, OneToOne, ManyToMany, Foreign]


def delete_all():
    for model in MODELS:
        model.objects.all().delete()


def create_samples():
    real_1 = Real.objects.create(a='A')
    real_2 = Real.objects.create(a='B')
    real_3 = Real.objects.create(a='C')
    Proxy.objects.create(a='D')
    Sub.objects.create(a='E', b=True)
    SubSub.objects.create(a='F', b=False, c='x')

    o2o_1 = OneToOne.objects.create(d='1.1')
    OneToOne.objects.create(d='2.2', r=real_1)
    o2o_3 = OneToOne.objects.create(d='3.3', r=real_2, s=o2o_1)
    OneToOne.objects.create(d='4.4', r=real_3, s=o2o_3)
    o2o_5 = OneToOne.objects.create(d='5.5')
    o2o_5.s = o2o_5
    o2o_5.save()

    ManyToMany.objects.create(e=1)
    m2m_2 = ManyToMany.objects.create(e=2)
    m2m_2.m.add(real_1)
    # m2m_3 = ManyToMany.objects.create(e=3)
    m2m_4 = ManyToMany.objects.create(e=4)
    m2m_4.m.add(real_1)
    # TODO: m2m_3.s.add(m2m_2)
    # m2m_4.s.add(m2m_3)
    # m2m_4.s.add(m2m_4)

    Foreign.objects.create(i=1)
    Foreign.objects.create(i=2, f=real_1)
    Foreign.objects.create(i=3, f=real_1)


def get_values_lists(*querysets):
    """
    Return a sorted list of model label, sorted values list tuples.
    When no querysets are defined, return values for all MODELS.
    When one or more querysets are defined, return all not included models as
    empty list and those from the querysets.
    """
    querysets_per_model = defaultdict(set)
    for queryset in querysets:
        querysets_per_model[queryset.model].add(queryset)

    values_lists = []
    for model in MODELS:
        values = []
        if model not in querysets_per_model:
            if not querysets:
                values.extend(model.objects.values_list())
        else:
            for queryset in querysets_per_model[model]:
                values.extend(queryset.values_list())

        values_lists.append((model_label(model), sorted(values)))
    return values_lists


@pytest.mark.django_db
def test_dump_load():
    delete_all()
    create_samples()

    expected_lists = get_values_lists()

    graph = ModelGraph()
    graph.add_queryset(Real.objects.all())
    # add also querysets for objects which don't touch Real objects.
    graph.add_queryset(OneToOne.objects.all())
    graph.add_queryset(ManyToMany.objects.all())
    graph.add_queryset(Foreign.objects.all())

    _, filename = tempfile.mkstemp()
    with open(filename, 'w+') as f:
        graph.dump_objects(f)
    with open(filename) as f:
        s = f.read()
    os.remove(filename)
    delete_all()

    graph = ModelGraph()
    graph.load_objects(s)

    actual_lists = get_values_lists()

    for actual, expected in zip(actual_lists, expected_lists):
        assert actual == expected


@pytest.mark.django_db
def test_dump_load_only_sub():
    delete_all()
    create_samples()
    sub_pks = list(Sub.objects.all().values_list('pk', flat=True))
    expected_lists = get_values_lists(Real.objects.filter(pk__in=sub_pks),
                                      Proxy.objects.filter(pk__in=sub_pks),
                                      Sub.objects.all(),
                                      SubSub.objects.filter(pk__in=sub_pks))

    graph = ModelGraph()
    graph.add_querysets(Sub.objects.all())

    _, filename = tempfile.mkstemp()
    with open(filename, 'w+') as f:
        graph.dump_objects(f)
    with open(filename) as f:
        s = f.read()
    os.remove(filename)
    delete_all()

    graph = ModelGraph()
    graph.load_objects(s)

    actual_lists = get_values_lists()

    for actual, expected in zip(actual_lists, expected_lists):
        assert actual == expected


@pytest.mark.django_db
def test_dump_load_only_sub_and_subsub():
    delete_all()
    create_samples()

    sub_pks = list(Sub.objects.all().values_list('pk', flat=True))
    expected_lists = get_values_lists(Real.objects.filter(pk__in=sub_pks),
                                      Proxy.objects.filter(pk__in=sub_pks),
                                      Sub.objects.all(),
                                      SubSub.objects.all())

    graph = ModelGraph()
    graph.add_querysets(Sub.objects.all(), SubSub.objects.all())

    _, filename = tempfile.mkstemp()
    with open(filename, 'w+') as f:
        graph.dump_objects(f)
    with open(filename) as f:
        s = f.read()
    os.remove(filename)
    assert 'F' in s
    delete_all()

    graph = ModelGraph()
    graph.load_objects(s)

    actual_lists = get_values_lists()

    for actual, expected in zip(actual_lists, expected_lists):
        assert actual == expected


@pytest.mark.django_db
def test_command_dump_load():

    delete_all()
    create_samples()
    queryset = OneToOne.objects.filter(d="5.5")
    expected_lists = get_values_lists(queryset)

    _, filename = tempfile.mkstemp()
    call_command('model_graph', filename,
                 querysets=['testapp-onetoone-filter(d="5.5")'])

    delete_all()
    call_command('model_graph', filename)
    os.remove(filename)

    actual_lists = get_values_lists()

    for actual, expected in zip(actual_lists, expected_lists):
        assert actual == expected
