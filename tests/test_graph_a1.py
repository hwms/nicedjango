from textwrap import dedent

import pytest
from django.utils import six

from nicedjango.graph import ModelGraph
from tests.a1.models import A, B, C
from tests.utils import delete_all, get_all_values


def reset_samples():
    delete_all()
    A.objects.create(name='a_1')
    B.objects.create(name='b_1')
    C.objects.create(name='c_1')
    C.objects.create(name='c_2')

EXPECTED_A = [
    {'id': 1, 'name': 'a_1'},
    {'id': 2, 'name': 'b_1'},
    {'id': 3, 'name': 'c_1'},
    {'id': 4, 'name': 'c_2'},
]


@pytest.mark.django_db
@pytest.mark.parametrize(('queries', 'extras', 'expected_dump', 'expected'), (
    (A, None, """\
        ---
        - a1.a: [id, name]
        - [1, a_1]
        - [2, b_1]
        - [3, c_1]
        - [4, c_2]
        """,
        {'a1.a': EXPECTED_A,
         }),
    ((A, B, C), None, """\
        ---
        - a1.a: [id, name]
        - [1, a_1]
        - [2, b_1]
        - [3, c_1]
        - [4, c_2]
        ---
        - a1.b: [a_ptr]
        - [2]
        - [3]
        - [4]
        ---
        - a1.c: [b_ptr]
        - [3]
        - [4]
        """,
        {'a1.a': EXPECTED_A,
         'a1.b':
            [{'a_ptr_id': 2, 'id': 2, 'name': 'b_1'},
             {'a_ptr_id': 3, 'id': 3, 'name': 'c_1'},
             {'a_ptr_id': 4, 'id': 4, 'name': 'c_2'}],
         'a1.c':
            [{'a_ptr_id': 3, 'b_ptr_id': 3, 'id': 3, 'name': 'c_1'},
             {'a_ptr_id': 4, 'b_ptr_id': 4, 'id': 4, 'name': 'c_2'}],
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
