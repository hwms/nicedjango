from operator import itemgetter

from nicedjango.utils.py import sliceable_as_chunks
from nicedjango.utils.py.chunk import as_chunks
from nicedjango.utils.py.iter import partition
from nicedjango.utils.py.operator import item_in

__all__ = ['partition_existing_pks', 'get_pks_queryset', 'queryset_as_chunks']


def partition_existing_pks(model, pk_index, values_list):
    queryset = get_pks_queryset(model)
    existing_pks = queryset_pk_in(queryset, map(itemgetter(pk_index), values_list))
    return partition(item_in(pk_index, existing_pks), values_list)


def get_pks_queryset(model):
    return model._default_manager.values_list(model._meta.pk.name, flat=True)


def queryset_pk_in(queryset, pks):
    return queryset_in(queryset, queryset.model._meta.pk.name, pks)


def queryset_in(queryset, name, values):
    filters = {'%s__in' % name: values}
    return queryset.filter(**filters)


def queryset_in_list_getter(queryset, name):
    def queryset_in_list_getter_(values):
        return list(queryset_in(queryset, name, values))
    return queryset_in_list_getter_


def queryset_as_chunks(queryset, chunksize=None, name=None, pks=None):
    if name is not None and pks is not None:
        values_getter = queryset_in_list_getter(queryset, name)
        for chunk in as_chunks(pks, chunksize, None, values_getter):
            yield chunk
    else:
        for chunk in sliceable_as_chunks(queryset, chunksize):
            yield chunk
