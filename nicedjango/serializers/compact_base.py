from django.core.serializers.base import Serializer as BaseSerializer
from django.core.serializers.base import DeserializedObject
from django.db import models
from django.db.models.fields.related import ManyToManyField
from django.utils import six

from nicedjango.utils import get_own_direct_fields_with_name, model_label
from nicedjango.utils.fields import get_pk_name


class Serializer(BaseSerializer):

    multiple_streams = False

    def __init__(self):
        self.model = None
        self.label = None
        self.names = []
        self.fields = []
        self._current = None
        self.first = True
        self.first_for_label = True

    def serialize(self, queryset, **options):
        """
        Serialize queryset.values_list().
        """
        self.options = options
        self.stream = options.pop("stream", six.StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)

        queryset = self.prepare_queryset(queryset)
        self.start_serialization()
        self.first = True
        for values in sorted(queryset):
            self._current = []
            for value, field in tuple(zip(values, self.fields)):
                value = self.handle_field_value(value, field)
                self._current.append(value)
            self.handle_values()
            self.first = False
            self.first_for_label = False
        self.end_serialization()
        return self.getvalue()

    def prepare_queryset(self, queryset):
        label = model_label(queryset.model._meta.concrete_model)
        self.first_for_label = self.label != label
        self.label = label
        # Use the concrete parent class' _meta instead of the object's _meta
        # This is to avoid local_fields problems for proxy models. Refs #17717.
        self.model = queryset.model._meta.concrete_model
        self.prepare_fields()
        return queryset.values_list(*self.names)

    def prepare_fields(self):
        pk = self.model._meta.pk
        self.names = [get_pk_name(self.model)]
        self.fields = [pk]
        for field in get_own_direct_fields_with_name(self.model).values():
            if (field.serialize and (self.selected_fields is None or
                                     field.name in self.selected_fields)):
                if isinstance(field, ManyToManyField):
                    if self.selected_fields:
                        raise ValueError('Compact serializer does not support '
                                         'm2m fields directly: %s' % field)
                    continue
                self.names.append(field.name)
                self.fields.append(field)

    def handle_field_value(self, value, field):
        raise NotImplementedError


class Deserializer(six.Iterator):

    """
    Abstract base deserializer class.
    """
    multiple_streams = False

    def __init__(self, stream_or_string, **options):
        """
        Init this serializer given a stream or a string
        """
        self.options = options
        if isinstance(stream_or_string, six.string_types):
            self.stream = six.StringIO(stream_or_string)
        else:
            self.stream = stream_or_string
        # hack to make sure that the models have all been loaded before
        # deserialization starts (otherwise subclass calls to get_model()
        # and friends might fail...)
        models.get_apps()

    def __iter__(self):
        return self

    def __next__(self):
        """Iteration iterface -- return the next item in the stream"""
        raise NotImplementedError


class DeserializedValuesObject(DeserializedObject):

    def __init__(self, model, label, names, values):
        self.model = model
        self.label = label
        self.names = names
        self.values = values
        # for backward compatibility
        self.m2m_data = None

    @property
    def object(self):
        "backward compatible on demand model creation"
        attnames = []
        for name in self.names:
            field, _, _, _ = self.model._meta.get_field_by_name(name)
            attnames.append(field.attname)
        return self.model(**dict(zip(attnames, self.values)))

    def __repr__(self):
        return "<DeserializedObject: %s.%s(pk=%s)>" % (
            self.model._meta.app_label, self.model._meta.object_name,
            self.values[0])
