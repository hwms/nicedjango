import logging
import os

from django.core import serializers

from nicedjango.utils import as_chunks, with_progress
from nicedjango.utils.py.iter import filter_attrs

log = logging.getLogger(__name__)


class Dumper(object):

    def __init__(self, sorted_nodes, serializer_name, chunksize=None, **options):
        self.chunksize = chunksize
        self.sorted_nodes = filter_attrs(sorted_nodes, 'pks')
        self.serializer = serializers.get_serializer(serializer_name)()
        self.options = options
        self.multiple_streams = getattr(self.serializer, 'multiple_streams', False)

        self.node = None
        self.stream = None

    def dump_to_single_stream(self, stream):
        self.stream = stream
        for progress, node in with_progress(self.sorted_nodes):
            log.info('dumping %d/%d models: %s', progress.pos, progress.size, node.label)
            self.dump_node(node)

    def start_stream(self, path, node=None):
        if self.stream is not None and (not self.multiple_streams or self.node == node):
            pass
        elif self.multiple_streams:
            if self.stream:
                self.stream.close()
            self.stream = open(self.get_filepath(path, node), 'wb+')
        else:
            self.stream = open(path, 'wb+')
        self.node = node

    def dump_to_path(self, path):
        try:
            for progress, node in with_progress(self.sorted_nodes):
                log.info('dumping %d/%d models: %s', progress.pos, progress.size, node.label)
                self.start_stream(path, node)
                self.dump_node(node)
        finally:
            self.stream.close()

    def get_filepath(self, path, node):
        return os.path.join(path, node.label.replace('.', '-') + '.csv')

    def dump_node(self, node):
        for pks in as_chunks(sorted(node.pks), self.chunksize):
            log.info('dumping chunk %d/%d (%d) of %s' % (pks.cpos, pks.csize, pks.size, node.label))
            queryset = node.model._default_manager.filter(**{'%s__in' % node.pk_name: pks})
            if self.serializer.internal_use_only and isinstance(self.stream, list):
                self.stream.extend(self.serializer.serialize(queryset, **self.options))
            else:
                self.serializer.serialize(queryset, stream=self.stream, **self.options)
