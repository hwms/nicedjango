import decimal

import yaml
from django.core.serializers import register_serializer
from django.db import models
from django.utils import six

from nicedjango.serializers import compact_python

# Use the C (faster) implementation if possible
try:
    from yaml import CSafeLoader as SafeLoader
    from yaml import CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper  # @UnusedImport

__all__ = ['CompactYamlSerializer', 'CompactYamlDeserializer']


class DjangoSafeDumper(SafeDumper):

    def represent_decimal(self, data):
        return self.represent_scalar('tag:yaml.org,2002:str', str(data))

DjangoSafeDumper.add_representer(decimal.Decimal,
                                 DjangoSafeDumper.represent_decimal)


class Serializer(compact_python.Serializer):
    """
    Serialize a queryset to compact YAML format:
    * one list of mixed model info and values:
    ** one entry dict in front of each model
    *** the dict has the model label as key, the fields as list
    ** lists of values for that model
    * first field and value are for the primary key
    * m2m dumps the intermediary table instead of lists of values
    """
    internal_use_only = False

    def start_serialization(self):
        pass

    def handle_values(self):
        if self.first_for_label:
            rows = [{self.label: self.names}, self._current]
        else:
            rows = [self._current]
        yaml.dump(rows, self.stream, Dumper=DjangoSafeDumper, **self.options)

    def handle_field_value(self, value, field):
        # avoid "!!python/time" type for TimeFields
        if isinstance(field, models.TimeField) and value is not None:
            return str(value)
        else:
            return super(Serializer, self).handle_field_value(value, field)

    def getvalue(self):
        # Grand-parent super
        return super(compact_python.Serializer, self).getvalue()

CompactYamlSerializer = Serializer


def parser(stream):
    lines = []
    for line in iter(stream.readline, ''):
        if len(lines) >= 1000 and line.startswith('-'):
            for obj in yaml.load(''.join(lines)):
                yield obj
            lines = []
        lines.append(line)
    for obj in yaml.load(''.join(lines), Loader=SafeLoader):
        yield obj


class Deserializer(compact_python.Deserializer):
    "Deserialize a stream or string of compact YAML into DeserializedValuesObject instances."

    def __init__(self, stream_or_string, **options):
        if isinstance(stream_or_string, bytes):
            stream_or_string = stream_or_string.decode('utf-8')
        if isinstance(stream_or_string, six.string_types):
            self.stream = six.StringIO(stream_or_string)
        else:
            self.stream = stream_or_string
        super(Deserializer, self).__init__(parser(self.stream), **options)

CompactYamlDeserializer = Deserializer

register_serializer('compact_yaml', __name__)
