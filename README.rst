nicedjango
==========

Nice django tools

|Build Status| |Coveralls| |Documentation Status| |Requirements Status|
|Downloads| |Latest Version| |Supported Python versions|
|Supported Python implementations| |Development Status| |Wheel Status|
|Egg Status| |Download format| |License|

_`ModelGraph`
=============
Selective dumping and loading of only the needed model data for all objects and their related
objects of one or more querysets.

This is done by

    * getting a graph of all relations between models,
    * getting all pks first in chunks,
    * dump them in an order that enables correct loading.

_`Examples`
-----------

::
   
   # show model graph parts that would be dumped and those which not:
   # example for query model a1.A with relation to child a1.B(A)
   ./manage.py dump_graph -p -q a -r a.b
       a1-a:
                  a1-a.b          to child            a1-b.pk
          excludes:
                  a1-a.f          to foreign          a1-f.a
        a1-b:
                  a1-b.pk         to parent           a1-a.pk
          excludes:
                  a1-b.c          to child            a1-c.pk
                  a1-b.e          to child            a1-e.pk
   
   # dump all objects from a1.models.A.objects.filter() with relation a.b as compact yaml:
   ./manage.py dump_graph -f dump.yaml -s compact_yaml -q a.filter(pk__in=(1,2)) -r a.b
       - a1-a: [pk]
        - [1]
        - [2]
        - a1-b: [pk]
        - [2]

   # load back the dumped dump.yaml
   ./manage.py load_graph -f dump.yaml -s compact_yaml
   
   # by default serializing into compact csv files is enabled:
   mkdir dump_folder
   ./manage.py dump_graph -f dump_folder -q a.filter(pk__in=(1,2)) -r a.b
   #results in two files under dump_folder:
   # a1-a.csv:
    a1-a:pk
    1
    2
   # and a1-b.csv:
    a1-b:pk
    2

.. |Build Status| image:: https://travis-ci.org/katakumpo/nicedjango.svg
   :target: https://travis-ci.org/katakumpo/nicedjango
.. |Coveralls| image:: https://coveralls.io/repos/katakumpo/nicedjango/badge.png?branch=master
   :target: https://coveralls.io/r/katakumpo/nicedjango?branch=master
.. |Downloads| image:: https://pypip.in/download/nicedjango/badge.svg
   :target: https://pypi.python.org/pypi/nicedjango/
.. |Latest Version| image:: https://pypip.in/version/nicedjango/badge.svg
   :target: https://pypi.python.org/pypi/nicedjango/
.. |Supported Python versions| image:: https://pypip.in/py_versions/nicedjango/badge.svg
   :target: https://pypi.python.org/pypi/nicedjango/
.. |Supported Python implementations| image:: https://pypip.in/implementation/nicedjango/badge.svg
   :target: https://pypi.python.org/pypi/nicedjango/
.. |Development Status| image:: https://pypip.in/status/nicedjango/badge.svg
   :target: https://pypi.python.org/pypi/nicedjango/
.. |Wheel Status| image:: https://pypip.in/wheel/nicedjango/badge.svg
   :target: https://pypi.python.org/pypi/nicedjango/
.. |Egg Status| image:: https://pypip.in/egg/nicedjango/badge.svg
   :target: https://pypi.python.org/pypi/nicedjango/
.. |Download format| image:: https://pypip.in/format/nicedjango/badge.svg
   :target: https://pypi.python.org/pypi/nicedjango/
.. |License| image:: https://pypip.in/license/nicedjango/badge.svg
   :target: https://pypi.python.org/pypi/nicedjango/
.. |Documentation Status| image:: https://readthedocs.org/projects/nicedjango-py/badge/?version=latest
   :target: https://nicedjango-py.readthedocs.org/en/latest/
.. |Codeship| image:: https://www.codeship.io/projects/c6e982d0-493e-0132-73e9-7e9eac026bf8/status
   :target: https://www.codeship.io/projects/46084
.. |Requirements Status| image:: https://requires.io/github/katakumpo/nicedjango/requirements.svg?branch=master
   :target: https://requires.io/github/katakumpo/nicedjango/requirements/?branch=master
