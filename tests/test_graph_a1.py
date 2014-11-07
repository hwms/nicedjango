import pytest

from nicedjango._compat import BytesIO
from nicedjango.graph import ModelGraph
from tests.a1.models import A, B, C
from tests.utils import delete_all, get_all_values


def reset_samples():
    delete_all()
    A.objects.create(name='a_1')
    B.objects.create(name='b_1')
    C.objects.create(name='c_1')
    C.objects.create(name='c_2')


@pytest.mark.django_db
@pytest.mark.parametrize(('queries', 'extras', 'expected'), (
    (A, None,
     {'a1': {'a': [{'id': 1, 'name': 'a_1'}, {'id': 2, 'name': 'b_1'},
                   {'id': 3, 'name': 'c_1'}, {'id': 4, 'name': 'c_2'}]}}
     ),
    ((A, B, C), None,
     {'a1': {'a': [{'id': 1, 'name': 'a_1'}, {'id': 2, 'name': 'b_1'},
                   {'id': 3, 'name': 'c_1'}, {'id': 4, 'name': 'c_2'}],
             'b': [{'a_ptr_id': 2, 'id': 2, 'name': 'b_1'},
                   {'a_ptr_id': 3, 'id': 3, 'name': 'c_1'},
                   {'a_ptr_id': 4, 'id': 4, 'name': 'c_2'}],
             'c': [{'a_ptr_id': 3, 'b_ptr_id': 3, 'id': 3, 'name': 'c_1'},
                   {'a_ptr_id': 4, 'b_ptr_id': 4, 'id': 4, 'name': 'c_2'}]}}
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
