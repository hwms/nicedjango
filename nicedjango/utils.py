from collections import defaultdict, Iterable

from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ModelBase
from django.db.models.fields.related import RelatedField
from django.db.models.loading import get_app, get_apps, get_model, get_models
from django.db.models.query import QuerySet
from django.db.models.related import RelatedObject
from nicedjango._compat import basestring, izip_longest, OrderedDict

__all__ = ['chunked', 'model_label']


def model_label(model_or_object):
    if isinstance(model_or_object, ModelBase):
        return '%s.%s' % (model_or_object._meta.app_label,
                          model_or_object._meta.object_name.lower())
    return model_or_object

_marker = object()


def quiet_get_model(*args, **kwargs):
    try:
        return get_model(*args, **kwargs)
    except LookupError:
        return None


def chunked(iterable, n):
    """
    Break an iterable into lists of a given length::
        >>> list(chunked([1, 2, 3, 4, 5, 6, 7], 3))
        [[1, 2, 3], [4, 5, 6], [7]]
    If the length of ``iterable`` is not evenly divisible by ``n``, the last
    returned list will be shorter.
    This is useful for splitting up a computation on a large number of keys
    into batches, to be pickled and sent off to worker processes. One example
    is operations on rows in MySQL, which does not implement server-side
    cursors properly and would otherwise load the entire dataset into RAM on
    the client.

    Copied from more_itertools:
        https://github.com/erikrose/more-itertools
    """
    # Doesn't seem to run into any number-of-args limits.
    for group in (list(g) for g in izip_longest(*[iter(iterable)] * n,
                                                fillvalue=_marker)):
        if group[-1] is _marker:
            # If this is the last group, shuck off the padding:
            del group[group.index(_marker):]
        yield group


class RememberingSet(set):

    def __init__(self, *args, **kwargs):
        super(RememberingSet, self).__init__(*args, **kwargs)
        self._memory = set()

    def add(self, value):
        if value not in self._memory and value not in self:
            super(RememberingSet, self).add(value)
            self._memory.add(value)

    def clear_memory(self):
        self._memory.clear()


def coerce_tuple(arg, *excludes):
    """
    If the argument *arg* is:
    * None, return empty tuple
    * an Iterable but not instance of *excludes*, by default (basestring,)
    * anything else as one element tuple
    """
    excludes = excludes or (basestring,)
    if arg is None:
        result = ()
    elif isinstance(arg, Iterable) and not isinstance(arg, excludes):
        result = tuple(arg)
    else:
        result = (arg,)
    return result


def get_modelname_appnames_dict():
    dct = defaultdict(set)
    for app in get_apps():
        for model in get_models(app):
            dct[model.__name__.lower()].add(model._meta.app_label)
    return dct


def divide_string(s, char='.'):
    """
    Divide string *s* by first occurence of *char* and return tuple of two
    strings or raise ValueErrors, when
    * *s* is no string
    * *s* is empty
    * *s* starts with *char*
    """
    if not isinstance(s, basestring):
        raise ValueError('must be a string: %s' % s)
    if not s:
        raise ValueError('can\'t be empty')
    if s.startswith(char):
        raise ValueError('can\'t start with %s: %s' % (char, s))
    divided = s.split(char, 1)
    if len(divided) == 1:
        return s, ''
    return divided


def get_unique_model_by_name(modelname, default=_marker):
    modelname = modelname.lower()
    appnames = get_modelname_appnames_dict().get(modelname, ())
    try:
        if len(appnames) > 1:
            raise ValueError('multiple apps (%) contain model %s' %
                             (','.join(appnames), modelname))
        elif not appnames:
            raise ValueError('model %s not found' % modelname)
    except ValueError as e:
        if default is _marker:
            raise e
        return default
    return quiet_get_model(tuple(appnames)[0], modelname)


def divide_model_def(model_def):
    """
    If models are defined A in app x and B in app y and z:
        * return (x.A, '') on *model_def* in (x.A, 'x.a', 'a')
        * return (x.A, 'foo.bar') on *model_def* in ('x.a.foo.bar',
                                                     'a.foo.bar')
        * return (y.B, '') on +model_def* in (y.B, 'y.b')
        * return (y.B, 'foo.bar') on *model_def* == 'y.b.foo.bar'
        * return (z.B, '') on +model_def* in (z.B, 'z.b')
        * return (z.B, 'foo.bar') on *model_def* == 'z.b.foo.bar'
        * raise ValueError on _def in
            ('b', 'b.foo', 'b.foo.bar', 'x', 'x.foo', 'x.foo.bar', object())
    """
    if isinstance(model_def, ModelBase):
        return model_def, ''
    if not isinstance(model_def, basestring):
        raise ValueError('definition must be string or Model: %s' % model_def)
    first, rest = divide_string(model_def)
    model = get_unique_model_by_name(first, None)
    try:
        app = get_app(first)
    except ImproperlyConfigured:
        app = None
    if model:
        if not app or not rest:
            return model, rest
    modelname, rest = divide_string(rest)
    model = quiet_get_model(first, modelname)
    if not model:
        raise ValueError('app or model %s not found' % model_def)
    return model, rest


def queryset_from_def(queryset_def):
    if isinstance(queryset_def, QuerySet):
        return queryset_def
    model, rest = divide_model_def(queryset_def)
    if not rest:
        return model._default_manager.all()
    # use eval to avoid redefining djangos queryset methods in text form
    return eval('model._default_manager.%s' % rest)


def get_related_object_from_def(rel_def):
    model, field = divide_model_def(rel_def)
    fields = model._meta.get_all_field_names()
    if field not in fields:
        raise ValueError('field %s not in %s at %s' % (field, fields, model))
    robj, _, _, _ = model._meta.get_field_by_name(field)
    if not isinstance(robj, RelatedObject):
        raise ValueError('field %s is no related object.' % robj)
    return robj


def get_own_related_infos(m):
    """
    Return all own fields as tuples:
       <field name>, <model related to>, <field name on related model>
       <relfield is primary key> <is relation>
    """
    per_robj = OrderedDict()
    # filter the shortest fieldname per related object (dj17 defines two)
    for fieldname in m._meta.get_all_field_names():
        robj, model, _, _ = m._meta.get_field_by_name(fieldname)

        if model:
            continue

        if robj in per_robj and len(per_robj[robj][0]) < len(fieldname):
            continue

        if isinstance(robj, RelatedField):
            per_robj[robj] = (fieldname, robj.rel.to,
                              robj.related_query_name(),
                              robj.primary_key, False)
        elif isinstance(robj, RelatedObject):
            per_robj[robj] = (fieldname, robj.field.model, robj.field.name,
                              robj.field.primary_key, True)
    return list(per_robj.values())
