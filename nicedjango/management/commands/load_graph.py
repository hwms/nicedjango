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

from django.core.management.base import BaseCommand, CommandError

from nicedjango.graph import ModelGraph

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-f', '--filepath', action='store',
                    help='(File-)path to load from.'),
        make_option('-c', '--chunksize', action='store', type=int,
                    default=1000, help='Maximum chunk size for queries'),
        make_option('-s', '--serializer', action='store', default='compact_csv',
                    choices=('compact_yaml', 'compact_csv'),
                    help='Serializer to be used.'),
    )
    help = __doc__

    def handle(self, **options):
        filepath = options['filepath']
        chunksize = options['chunksize']

        if not filepath:
            raise CommandError('No filepath (-f) to load from given.')
        graph = ModelGraph(chunksize=chunksize)
        graph.load_from_path(options['serializer'], filepath)
