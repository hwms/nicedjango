from __future__ import unicode_literals

from django.conf import settings
from django.core.serializers.base import DeserializationError
from django.db import DEFAULT_DB_ALIAS, models
from django.utils.encoding import is_protected_type, smart_text

from nicedjango.serializers import compact_base
from nicedjango.serializers.compact_base import DeserializedValuesObject


class Serializer(compact_base.Serializer):

    """
    Serializes a QuerySet to basic Python objects.
    """
    internal_use_only = True

    def handle_field_value(self, value, field):
        # Protected types (i.e., primitives like None, numbers, dates,
        # and Decimals) are passed through as is. All other values are
        # converted to string first.
        if is_protected_type(value):
            return value
        else:
            return smart_text(value)

    def handle_fk_field_value(self, value, field):
        return value

    def getvalue(self):
        return [self.names] + self.rows


def Deserializer(compact_values, **options):
    """
    Deserialize compact Python values back into Django ORM instances.

    compact_values are in the form of:

        [{model_label: [pk_name, field_name_1, field_name_2,..]},
         [pk_1, value_1_1, value_2_1],
         [pk_2, value_1_2, value_2_2],
         {another_model_label: [..]},
         [..]]
    """
    options.pop('using', DEFAULT_DB_ALIAS)
    ignore = options.pop('ignorenonexistent', False)
    encoding = options.get("encoding", settings.DEFAULT_CHARSET)
    models.get_apps()

    model = None
    names = None

    for values in compact_values:
        if isinstance(values, dict):
            label, names = tuple(values.items())[0]
            model = _get_model(label)
            actual_names = model._meta.get_all_field_names()
            if ignore:
                names = list(filter(lambda n: n in actual_names, names))
            continue
        values_ = []
        for value in values:
            if isinstance(value, str):
                value = smart_text(value, encoding, strings_only=True)
            values_.append(value)

        yield DeserializedValuesObject(model, names, values_)


def _get_model(model_identifier):
    """
    Helper to look up a model from an "app_label.model_name" string.
    """
    try:
        Model = models.get_model(*model_identifier.split("."))
    except TypeError:
        Model = None
    if Model is None:
        raise DeserializationError(
            "Invalid model identifier: '%s'" %
            model_identifier)
    return Model
