import glob
import logging
import os
from operator import attrgetter
from time import time

from django.core import serializers

from nicedjango.graph.utils import sort_nodes
from nicedjango.serializers.compact_csv import parser
from nicedjango.utils import as_chunks
from nicedjango.utils.bulk import bulk_replace_values
from nicedjango.utils.py.iter import map_attr

log = logging.getLogger(__name__)


class Loader(object):

    def __init__(self, graph, serializer_name, **options):
        self.graph = graph
        self.deserializer = serializers.get_deserializer(serializer_name)
        self.options = options
        self.multiple_streams = getattr(self.deserializer, 'multiple_streams', False)
        self.stream = None

    def load_from_path(self, path):
        for filepath in self.get_filepaths(path):
            with open(filepath) as stream:
                self.load_from_stream(stream)

    def get_filepaths(self, path):
        if self.multiple_streams:
            paths_per_node = dict()
            for filepath in glob.iglob(os.path.join(path, '*.csv')):
                node = self.add_node_from_filepath(filepath)
                paths_per_node[node] = filepath
            sorted_nodes = filter(paths_per_node.__contains__,
                                  sort_nodes(self.graph.nodes.values()))
            return list(map(paths_per_node.get, sorted_nodes))
        return [path]

    def add_node_from_filepath(self, filepath):
        with open(filepath) as stream:
            head = next(parser(stream, **self.options))
            label = list(head.items())[0][0]
        return self.graph.add_node(label)

    def load_from_stream(self, stream, **options):
        for objs in as_chunks(self.deserializer(stream), self.graph.chunksize, attrgetter('label')):
            self.load_objects(objs)

    def load_objects(self, objs):
        obj = objs[0]
        msg = '%20s %12d to %12d:' % (obj.label, objs.pos, objs.to_pos)
        log.info('Load %s %0.4f /%6d = %0.4f/obj', msg, objs.duration, objs.len, objs.per_obj)
        start = time()
        try:
            bulk_replace_values(list(map_attr(objs, 'values')), obj.model, obj.names)
        finally:
            duration = time() - start
            log.info('Save %s %0.4f /%6d = %0.4f/obj', msg, duration, objs.len, duration / objs.len)
