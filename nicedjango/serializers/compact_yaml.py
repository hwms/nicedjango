"""
YAML serializer.

Requires PyYaml (http://pyyaml.org/), but that's checked for in __init__.
"""

import decimal
import sys
from io import StringIO

import yaml
from django.core.serializers import register_serializer
from django.core.serializers.base import DeserializationError
from django.db import models
from django.utils import six
from yaml.events import (DocumentStartEvent, MappingStartEvent, ScalarEvent,
                         SequenceEndEvent, SequenceStartEvent)

from nicedjango.serializers import compact_python

# Use the C (faster) implementation if possible
try:
    from yaml import CSafeLoader as SafeLoader
    from yaml import CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper


class DjangoSafeDumper(SafeDumper):

    def represent_decimal(self, data):
        return self.represent_scalar('tag:yaml.org,2002:str', str(data))

DjangoSafeDumper.add_representer(decimal.Decimal,
                                 DjangoSafeDumper.represent_decimal)


class Serializer(compact_python.Serializer):

    """
    Convert a queryset to comact YAML format:
    * documents are equivalent to models
    * documents contain only one list with:
    ** one one entry dict in front
    *** the dict has the model label as key, the fields as list
    ** only list of values after the first entry
    * first field and value are the primary key
    * m2m dumps the intermediary table instead of lists of values

    """

    internal_use_only = False

    def start_serialization(self):
        yaml.dump([{self.label: self.names}], self.stream,
                  Dumper=DjangoSafeDumper, explicit_start=True,
                  **self.options)

    def handle_values(self):
        yaml.dump([self._current], self.stream, Dumper=DjangoSafeDumper,
                  **self.options)

    def handle_field_value(self, value, field):
        # avoid "!!python/time" type for TimeFields
        if isinstance(field, models.TimeField) and value is not None:
            return str(value)
        else:
            super(Serializer, self).handle_field_value(value, field)

    def getvalue(self):
        # Grand-parent super
        return super(compact_python.Serializer, self).getvalue()


def parser(stream):
    generator = yaml.parse(stream, Loader=SafeLoader)
    sequence_depth = 0
    in_mapping = False
    label = None
    values = []
    for event in generator:
        if isinstance(event, DocumentStartEvent):
            in_mapping = False
            label = None
            values = []
        elif isinstance(event, ScalarEvent):
            value = event.value
            if not event.implicit[1]:
                value = yaml.load(value, Loader=SafeLoader)
            if sequence_depth == 1 and in_mapping:
                label = value
            if sequence_depth == 2:
                values.append(value)
        elif isinstance(event, MappingStartEvent):
            in_mapping = True
        elif isinstance(event, SequenceStartEvent):
            sequence_depth += 1
        elif isinstance(event, SequenceEndEvent):
            sequence_depth -= 1
            if sequence_depth == 1:
                if in_mapping:
                    in_mapping = False
                    yield {label: values}
                    label = None
                    values = []
                else:
                    yield values
                values = []


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of YAML data.
    """
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode('utf-8')
    if isinstance(stream_or_string, six.string_types):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    try:
        for obj in compact_python.Deserializer(parser(stream), **options):
            yield obj

    except GeneratorExit:
        raise
    except Exception as e:
        # Map to deserializer error
        six.reraise(DeserializationError, DeserializationError(e),
                    sys.exc_info()[2])

register_serializer('compact_yaml', __name__)
