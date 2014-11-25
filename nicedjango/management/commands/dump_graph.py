"""
Selective dumping and loading of only the needed model data for all objects and their related
objects of one or more querysets.

This is done by

    * getting a graph of all relations between models,
    * getting all pks first in chunks,
    * dump them in an order that enables correct loading.

"""
import logging
from optparse import make_option

from django.core.management.base import BaseCommand

from nicedjango.graph import ModelGraph

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-f', '--filepath', action='store',
                    help='(File-)path to dump to.'),
        make_option('-q', '--queries', action='append',
                    help='Queries in the form of [<app>.]<model> or'
                         ' [<app>.]<model>.<queryset method calls>'),
        make_option('-r', '--relations', action='append',
                    help='Extra relations to be queried in the form of'
                         ' [<app>.]<model>.<field>'),
        make_option('-p', '--print', action='store_true',
                    help='Print the graph that would be queried'),
        make_option('-c', '--chunksize', action='store', type=int,
                    default=1000, help='Maximum chunk size for queries'),
        make_option('-s', '--serializer', action='store', default='compact_csv',
                    choices=('compact_yaml', 'compact_csv'),
                    help='Serializer to be used.'),
    )
    help = __doc__

    def handle(self, **options):
        filepath = options['filepath']
        queries = options['queries'] or []
        relations = options['relations'] or []
        chunksize = options['chunksize']

        graph = ModelGraph(queries, relations, chunksize=chunksize)
        if options['print']:
            graph.print_graph()
        if filepath:
            graph.dump_to_path(options['serializer'], filepath)
