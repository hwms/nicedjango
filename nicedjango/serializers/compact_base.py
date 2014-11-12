"""
Module for abstract serializer/unserializer base classes.
"""
from django.core.serializers.base import Serializer as BaseSerializer
from django.core.serializers.base import DeserializedObject
from django.db import models
from django.utils import six

from nicedjango.utils import model_label


class Serializer(BaseSerializer):

    """
    Abstract compact serializer base class.
    """

    def serialize(self, queryset, **options):
        """
        Serialize queryset.values_list().
        """
        self.options = options

        self.stream = options.pop("stream", six.StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)

        self.model = None
        self.label = None
        self.names = []
        self.fields = []
        self.handles = []
        self._current = None

        queryset = self.prepare_queryset(queryset)
        self.start_serialization()
        self.first = True
        for values in queryset:
            for value, field, handle in tuple(zip(values, self.fields,
                                                  self.handles)):
                handle(value, field)
            self._current = values
            self.handle_values()
            if self.first:
                self.first = False
        self.end_serialization()
        return self.getvalue()

    def prepare_queryset(self, queryset):
        # Use the concrete parent class' _meta instead of the object's _meta
        # This is to avoid local_fields problems for proxy models. Refs #17717.
        self.model = queryset.model._meta.concrete_model
        self.label = model_label(queryset.model)
        self.prepare_fields()
        return queryset.values_list(*self.names)

    def prepare_fields(self):
        pk = self.model._meta.pk
        self.names = [pk.name]
        self.fields = [pk]
        self.handles = []
        for field in self.model._meta.local_fields:
            if field.serialize:
                if field.rel is None:
                    if (self.selected_fields is None or
                            field.name in self.selected_fields):
                        self.names.append(field.name)
                        self.fields.append(field)
                        self.handles.append(self.handle_field_value)
                else:
                    if (self.selected_fields is None or
                            field.name[:-3] in self.selected_fields):
                        self.names.append(field.name)
                        self.fields.append(field)
                        self.handles.append(self.handle_fk_field_value)
        for field in self.model._meta.many_to_many:
            if (field.serialize and self.selected_fields is not None
                    and field.name in self.selected_fields):
                raise ValueError('Compact serializer does not support'
                                 'serialization of m2m fields directly.'
                                 'm2m field: %s' % field)

    def start_serialization(self):
        """
        Called when serializing of the queryset starts.
        """
        raise NotImplementedError

    def end_serialization(self):
        """
        Called when serializing of the queryset ends.
        """
        pass

    def handle_values(self):
        """
        Called when serializing a rowof an object starts.
        """
        raise NotImplementedError

    def end_object(self):
        """
        Called when serializing of an object ends.
        """
        pass

    def handle_field_value(self, value, field):
        """
        Called to handle each individual (non-relational) field on an object.
        """
        raise NotImplementedError

    def handle_fk_field_value(self, value, field):
        """
        Called to handle a ForeignKey field.
        """
        raise NotImplementedError

    def getvalue(self):
        """
        Return the fully serialized queryset (or None if the output stream is
        not seekable).
        """
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()


class Deserializer(six.Iterator):

    """
    Abstract base deserializer class.
    """

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

    def __init__(self, model, names, values):
        self.model = model
        self.names = names
        self.values = values
        # for backward compatibility
        self.m2m_data = None

    @property
    def object(self):
        # backward compatible on demand model creation
        return self.model(**dict(zip(self.names, self.values)))

    def __repr__(self):
        return "<DeserializedObject: %s.%s(pk=%s)>" % (
            self.model._meta.app_label, self.model._meta.object_name,
            self.values[0])
