from __future__ import unicode_literals

from django.conf import settings
from django.core.serializers import register_serializer
from django.core.serializers.base import Deserializer as BaseDeserializer
from django.db import DEFAULT_DB_ALIAS
from django.utils.encoding import is_protected_type, smart_text

from nicedjango.serializers import compact_base
from nicedjango.serializers.compact_base import DeserializedValuesObject
from nicedjango.utils import model_by_label, model_label

__all__ = ['CompactPythonSerializer', 'CompactPythonDeserializer']


class Serializer(compact_base.Serializer):

    internal_use_only = True

    def start_serialization(self):
        self.rows = []

    def handle_values(self):
        if self.first_for_label:
            self.rows.append({self.label: self.names})
        self.rows.append(self._current)

    def handle_field_value(self, value, field):
        # Protected types (i.e., primitives like None, numbers, dates,
        # and Decimals) are passed through as is. All other values are
        # converted to string first.
        if is_protected_type(value):
            return value
        else:
            return smart_text(value)

    def getvalue(self):
        return self.rows

CompactPythonSerializer = Serializer


class Deserializer(BaseDeserializer):
    """
    Deserialize compact Python values into DeserializedValuesObject instances.

    compact_values_iterable is in the form of:

        [{model_label: [pk_name, field_name_1, field_name_2,..]},
         [pk_1, value_1_1, value_2_1],
         [pk_2, value_1_2, value_2_2],
         {another_model_label: [..]},
         [..]]
    """

    def __init__(self, compact_values_iterable, **options):
        super(Deserializer, self).__init__(compact_values_iterable, **options)
        self.options.pop('using', DEFAULT_DB_ALIAS)
        self.ignore = options.pop('ignorenonexistent', False)
        self.encoding = options.get("encoding", settings.DEFAULT_CHARSET)

        self.label = None
        self.model = None
        self.names = None
        self.iterator = iter(compact_values_iterable)

    def __next__(self):
        compact_values = next(self.iterator)
        while not compact_values or isinstance(compact_values, dict):
            self.label, self.names = tuple(compact_values.items())[0]
            self.model = model_by_label(self.label)._meta.concrete_model
            self.label = model_label(self.model)
            if self.ignore:
                actual = self.model._meta.get_all_field_names()
                self.names = list(filter(actual.__contains__, self.names))
            compact_values = next(self.iterator)

        values = []
        for value in compact_values:
            if isinstance(value, str):
                value = smart_text(value, self.encoding, strings_only=True)
            values.append(value)

        return DeserializedValuesObject(self.model, self.label, self.names,
                                        values)
CompactPythonDeserializer = Deserializer

register_serializer('compact_yaml', __name__)
