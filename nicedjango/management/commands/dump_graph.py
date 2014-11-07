"""
Selective dumping and loading of only the needed model data for all objects and
their related objects of one or more querysets.

This is done by

    * getting a graph of all relations between models,
    * than getting all pks first chunked in steps of 10k
    * and than dump them in an order that enables correct loading.

For now the serialization is handled by django's yaml decoder to enable queries
in chunks for big data.
"""
import logging
from optparse import make_option

from django.core.management.base import BaseCommand
from nicedjango.graph import ModelGraph

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dumpfile', action='store',
                    help='File to dump to'),
        make_option('-q', '--querysets', action='append',
                    help='Queryset\'s in the form of <app>.<model> or'
                         ' <app>.<model>.<queryset method calls>'),
        make_option('-e', '--extra-rels', action='append',
                    help='Extra relations to be queried in the form of'
                         ' <app>.<model>.<field>'),
        make_option('-s', '--show', action='store_true',
                    help='Show the to graph that would be queried'),
    )
    help = __doc__

    def handle(self, **options):
        show = options['show']
        dumpfile = options['dumpfile']
        queryset_defs = options['querysets'] or []
        extra_rel_defs = options['extra_rels'] or []

        graph = ModelGraph(queryset_defs, extra_rel_defs)
        if show:
            graph.show()
        if dumpfile:
            with open(dumpfile, 'w+') as outfile:
                graph.dump_objects(outfile)
