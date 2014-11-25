from collections import OrderedDict
from operator import attrgetter

from django.db.models.fields.related import RelatedField
from django.db.models.related import RelatedObject

from nicedjango._compat import exclude

__all__ = ['db_prep_values_list', 'db_prep_values', 'get_fields_dict',
           'get_own_direct_fields_with_name', 'get_quoted_columns',
           'iter_all_fields_with_name', 'iter_own_fields_with_name']


def get_pk_name(model):
    if 'pk' not in model._meta.get_all_field_names():
        return 'pk'
    return model._meta.pk and model._meta.pk.name or None


def db_prep_values_list(fields, connection, values_list):
    for values in values_list:
        yield list(db_prep_values(fields, connection, values))


def db_prep_values(fields, connection, values):
    for field, value in zip(fields, values):
        yield field.get_db_prep_save(value, connection)


def get_fields_dict(model, names, expect_pk=True):
    fields_dict = get_own_direct_fields_with_name(model)
    fields = fields_dict.values()
    if expect_pk and model._meta.pk not in fields:
        raise ValueError('pk %s not in %s' % (model._meta.pk.name, names))
    names_not_in = list(exclude(fields_dict.__contains__, names))
    if names_not_in:
        raise ValueError('Fields %s missing in %s.' % (names_not_in, model))
    return OrderedDict(zip(names, map(fields_dict.get, names)))


def get_quoted_columns(connection, fields):
    return list(map(connection.ops.quote_name,
                    map(attrgetter('column'), fields)))


def get_own_direct_fields_with_name(model):
    fields = OrderedDict()
    for name, field, direct, _, _ in iter_own_fields_with_name(model):
        if direct:
            fields[name] = field
    return fields


def iter_own_fields_with_name(model):
    "Filter related fields and duplicates from dj17."
    names = OrderedDict()
    for name, field, model_, direct, m2m in iter_all_fields_with_name(model):
        if model_:
            continue
        if field == model._meta.pk:
            name = get_pk_name(model)
        is_rel = False
        if isinstance(field, (RelatedField, RelatedObject)):
            field = direct and field or field.field
            is_rel = True
        result = (field, direct, m2m, is_rel)
        if result in names and len(names[result]) < len(name):
            # filters the shortest name per robj (dj17 defines two)
            continue
        names[result] = name
    for (field, direct, m2m, is_rel), name in names.items():
        yield name, field, direct, m2m, is_rel


def iter_all_fields_with_name(model):
    for name in model._meta.get_all_field_names():
        field, model_, direct, m2m = model._meta.get_field_by_name(name)
        yield name, field, model_, direct, m2m
