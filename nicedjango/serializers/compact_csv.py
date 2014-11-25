from __future__ import unicode_literals

from django.core.serializers import register_serializer
from django.utils import six
from django.utils.encoding import smart_text

from nicedjango.serializers import compact_python
from nicedjango.utils.compact_csv import CsvReader, quote_value

__all__ = ['CompactCsvSerializer', 'CompactCsvDeserializer']


class Serializer(compact_python.Serializer):

    internal_use_only = False
    multiple_streams = True

    def start_serialization(self):
        pass

    def handle_values(self):
        if self.first_for_label:
            self.writeline('%s:%s' % (self.label, ','.join(self.names)))
        self.writerow(self._current)

    def writeline(self, value):
        self.stream.write(('%s\n' % smart_text(value)).encode('utf-8'))

    def writerow(self, row):
        self.writeline(','.join(row))

    def handle_field_value(self, value, field):
        return quote_value(value)

    handle_fk_field_value = handle_field_value

    def getvalue(self):
        # Grand-parent super
        return super(compact_python.Serializer, self).getvalue()

CompactCsvSerializer = Serializer


def parser(stream, **options):
    reader = CsvReader(stream)
    headers = reader.next()
    label, pk = headers[0].split(':')
    yield {label: [pk] + headers[1:]}
    for row in reader:
        yield row


class Deserializer(compact_python.Deserializer):
    "Deserialize a stream or string of compact CSV into DeserializedValuesObject instances."
    multiple_streams = True

    def __init__(self, stream_or_string, **options):
        if isinstance(stream_or_string, bytes):
            stream_or_string = stream_or_string.decode('utf-8')
        if isinstance(stream_or_string, six.string_types):
            self.stream = six.StringIO(stream_or_string)
        else:
            self.stream = stream_or_string
        super(Deserializer, self).__init__(parser(self.stream), **options)
CompactCsvDeserializer = Deserializer

register_serializer('compact_csv', __name__)
