from collections import defaultdict

from django.db.models.base import ModelBase
from django.db.models.loading import get_apps, get_models
from django.db.models.query import QuerySet

from nicedjango._compat import basestring
from nicedjango.utils.py.string import divide_string

_APP_NAMES_CACHE = defaultdict(set)
_MODEL_CACHE = {}


def _cache():
    if _APP_NAMES_CACHE:
        return
    for app in get_apps():
        for model in get_models(app, include_auto_created=True):
            model_name = model._meta.object_name.lower()
            app_name = model._meta.app_label.lower()
            _APP_NAMES_CACHE[model_name].add(app_name)
            _MODEL_CACHE[model_label(model)] = model
    for model_name, app_labels in _APP_NAMES_CACHE.items():
        if len(app_labels) == 1:
            model = _MODEL_CACHE[model_label(list(app_labels)[0], model_name)]
            _MODEL_CACHE[model_name] = model


def model_label(first, second=None):
    if isinstance(first, ModelBase):
        second = first._meta.object_name.lower()
        first = first._meta.app_label
    if isinstance(first, basestring) and isinstance(second, basestring):
        return '%s-%s' % (first, second)
    return first

_marker = object()


def model_by_label(label, default=_marker):
    if isinstance(label, ModelBase):
        return label
    _cache()
    model = _MODEL_CACHE.get(label.lower(), default)
    if model is _marker:
        raise ValueError('model %s not found' % label)
    return model


def divide_model_def(model_def):
    """
    If models are defined A in app x and B in app y and z:
        * return (x.A, '') on *model_def* in (x.A, 'x-a', 'a')
        * return (x.A, 'foo.bar') on *model_def* in ('x-a.foo.bar',
                                                     'a.foo.bar')
        * return (y.B, '') on *model_def* in (y.B, 'y-b')
        * return (y.B, 'foo.bar') on *model_def* == 'y-b.foo.bar'
        * return (z.B, '') on *model_def* in (z.B, 'z-b')
        * return (z.B, 'foo.bar') on *model_def* == 'z-b.foo.bar'
        * raise ValueError on _def in
            ('b', 'b.foo', 'b.foo.bar', 'x', 'x-foo', 'x-foo.bar', object())
    """
    if isinstance(model_def, ModelBase):
        return model_def, ''
    if not isinstance(model_def, basestring):
        raise ValueError('definition must be string or Model: %s' % model_def)
    first, rest = divide_string(model_def, '.')
    model = model_by_label(first)
    return model, rest


def queryset_from_def(queryset_def):
    if isinstance(queryset_def, QuerySet):
        return queryset_def
    model, rest = divide_model_def(queryset_def)
    if not rest:
        return model._default_manager.all()
    # use eval to avoid redefining djangos queryset methods in text form
    return eval('model._default_manager.%s' % rest)
