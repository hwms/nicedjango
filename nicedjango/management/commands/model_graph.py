"""
ModelGraph
==========
Selective dumping and loading of only the needed model data for all objects and
their related objects of one or more querysets.

This is done by

    * getting a graph of all relations between models,
    * than getting all pks first chunked in steps of 10k
    * and than dump them in an order that enables correct loading.

For now the serialization is handled by django's yaml decoder to enable queries
in chunks for big data.

Examples:

    # dump all objects from myapp.models.MyModel.objects.filter(..)
    ./manage.py model_graph dump.yaml -q 'myapp-mymodel-filter(..)'
    # load dump.yaml
    ./manage.py model_graph dump.yaml
"""
import logging
import sys
from optparse import make_option

from django.core.management.base import BaseCommand

from nicedjango.graph import ModelGraph

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
log = logging.getLogger(__name__)
log.addHandler(console)
log.setLevel(logging.INFO)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--querysets', action='append',
                    help='Queryset\'s in the form of:\n\t'
                         '<appname>.<modelname>.<filter calls>.'),
    )
    help = __doc__
    args = 'dumpfile'

    def handle(self, dumpfile, **options):
        graph = ModelGraph()
        if not options['querysets']:
            with open(dumpfile) as f:
                graph.load_objects(f)
        else:
            with open(dumpfile, 'w+') as f:
                graph.dump_objects(f, *options['querysets'])
