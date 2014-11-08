nicedjango
==========

Nice django tools

|Build Status| |Coveralls| |Documentation Status| |Requirements Status|
|Downloads| |Latest Version| |Supported Python versions|
|Supported Python implementations| |Development Status| |Wheel Status|
|Egg Status| |Download format| |License|

_`ModelGraph`
=============
Selective dumping and loading of only the needed model data for all
objects and their related objects of one or more querysets.

This is done by
 * getting a graph of all relations between models,
 * than getting all pks first chunked in steps of 10k
 * and than dump them in an order that enables correct loading.

For now the serialization is handled by django's yaml decoder to enable
queries in chunks for big data.

_`Examples`
-----------

::
   
   # show model graph parts that would be dumped and those which not:
   ./manage.py dump_graph -s -q 'a'
    a1.a:
      ignored subs:
        a1.a.b > a1.b
   
   # add relations to the to be dumped graph
   ./manage.py dump_graph -s -q 'a' -e 'a.b'
     a1.a:
       subs:
         a1.a.b > a1.b
     a1.b:
       parents:
         a1.b.a_ptr > a1.a
       ignored subs:
         a1.b.c > a1.c

   # dump all objects from myapp.models.MyModel.objects.filter(..)
   ./manage.py dump_graph -d dump.yaml -q 'myapp.mymodel.filter(..)'
   
   # load dump.yaml
   ./manage.py load_graph dump.yaml

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
