nicedjango
==========

Nice django tools

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
