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

from django.core.management.base import BaseCommand
from nicedjango.graph import ModelGraph

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = __doc__
    ARGS = 'loadfile'

    def handle(self, loadfile, **options):
        graph = ModelGraph()
        with open(loadfile) as infile:
            graph.load_objects(infile)
