from operator import attrgetter

from django.db.models.loading import get_app, get_models

from nicedjango._compat import exclude
from nicedjango.graph.utils import sort_nodes
from nicedjango.serializers.compact_python import Serializer
from nicedjango.utils import queryset_from_def
from nicedjango.utils.bulk import reset_tables

APPNAMES = ('a1', 'a2', 'a3')


def delete_all():
    for model in all_models():
        reset_tables(model)


def get_sorted_models(nodes):
    return list(map(attrgetter('model'), sort_nodes(nodes)))


def get_pydump(sorted_models):
    sorted_models = list(filter(is_concrete, sorted_models))
    sorted_models += list(exclude(sorted_models.__contains__, all_models()))
    return get_dump(Serializer(), sorted_models)


def get_text_pydump(pydump):
    lines = []
    model_vals = []
    for row in pydump:
        if isinstance(row, dict):
            if model_vals:
                lines.append('    %s' % ', '.join(model_vals))
                model_vals = []
            lines.append(
                '%s: %s' %
                (list(
                    row.keys())[0], ' '.join(
                    list(
                        row.values())[0])))
            model_vals = []
        else:
            model_vals.append(' '.join(map(str, row)))
    if model_vals:
        lines.append('    %s' % ', '.join(model_vals))
    return '\n'.join(lines)


def is_concrete(model):
    return not (model._meta.abstract or model._meta.proxy)


def all_models():
    for appname in APPNAMES:
        for model in filter(
                is_concrete, get_models(get_app(appname), include_auto_created=True)):
            yield model


def get_dump(serializer, queries):
    querysets = list(map(queryset_from_def, queries))
    actual_dump = []
    for queryset in querysets:
        actual_dump.extend(serializer.serialize(queryset))
    return actual_dump
