from itertools import starmap
import logging
from subprocess import call
from textwrap import dedent

import django
from django.conf import settings


DBS = {'sq': {'ENGINE': 'django.db.backends.sqlite3',
              'NAME': ':memory:',
              },
       'my': {'ENGINE': 'django.db.backends.mysql',
             'NAME': 'nicedjango',
             'USER': 'root',
             'OPTIONS': {
                 'init_command': 'SET storage_engine=INNODB; SET character_set_database=UTF8;',
                 'local_infile': 1
             },
},
    'pg': {'ENGINE': 'django.db.backends.postgresql_psycopg2',
           'USER': 'postgres',
           'NAME': 'nicedjango',
           'OPTIONS': {
               'autocommit': True,
           },
           },
}


def parametrize_args(metafunc, params_dict, **kwargs):
    "Parametrize by dict filtered and ordered by functions argnames."
    from nicedjango._compat import izip
    argnames = []
    params = []
    for name in metafunc.funcargnames:
        if name in params_dict:
            argnames.append(name)
            params.append(params_dict[name])

    metafunc.parametrize(argnames, list(izip(*params)), **kwargs)


def _prep_expected_samples_params(metafunc, ids):
    "Prep kwargs like expected, expected_no_nl, expected2_no_nl."
    for name, samples_dict in metafunc.function.graph.kwargs.items():
        if name.startswith('expected'):
            yield _prep_samples(name, samples_dict, ids)

def _prep_samples(name, samples_dict, ids):
    from nicedjango._compat import imap
    samples = list(imap(lambda i: dedent(samples_dict[i]), ids))
    if name.endswith('_no_nl'):
        samples = list(imap(lambda e: e[:-1], samples))
        name = name[:-6]
    return name, samples

def parametrize_graph_test(metafunc):
    """
    Graph tests can be automagically parametrized by this.
    For parameters .samples.SAMPLES is used as ids, queries and relations base.
    Additionally .samples_compact_python.SAMPLES_PYTHON is used to provide expected_dump.
    Optional one can give multiple other expected samples with:

        @pytest.mark.graph(expected[a-z0-9][_no_nl]=SAMPLES_XY)

    Values there will be dedented and last char will be stripped if expected.. ends in '_no_nl'.
    """
    from .samples import SAMPLES
    from .samples_compact_python import SAMPLES_PYTHON
    from nicedjango import ModelGraph
    from nicedjango._compat import imap
    from tests.utils import get_sorted_models
    params = {}
    params['test_id'] = ids = SAMPLES.keys()
    params['queries'], params['relations'] = zip(*SAMPLES.values())

    params.update(_prep_expected_samples_params(metafunc, ids))

    if 'expected_dump' in metafunc.funcargnames:
        params['expected_dump'] = _prep_samples('expected_no_nl', SAMPLES_PYTHON, ids)[1]

    if 'graph' in metafunc.funcargnames:
        params['graph'] = graphs = list(starmap(ModelGraph, SAMPLES.values()))

        if 'sorted_models' in metafunc.funcargnames:
            params['sorted_models'] = list(imap(lambda g: get_sorted_models(g.nodes.values()),
                                                     graphs))

    parametrize_args(metafunc, params, ids=ids)


def setup_graph_test(item):
    if hasattr(item.function, 'django_db'):
        from .samples import reset_samples
        reset_samples()


def pytest_generate_tests(metafunc):
    if hasattr(metafunc.function, 'graph'):
        parametrize_graph_test(metafunc)


def pytest_runtest_setup(item):
    item.session._setupstate.prepare(item)
    if hasattr(item.function, 'graph'):
        setup_graph_test(item)


def pytest_addoption(parser):
    parser.addoption("--db", action="store", choices=['sq', 'my', 'pg'], default='sq',
                     help="run with db")


def pytest_configure(config):
    db_conf = DBS[config.option.db]
    if config.option.db == 'my':
        call(['mysql', '-u', 'root', '-e', 'create database if not exists nicedjango;'])
    elif config.option.db == 'pg':
        call(['psql', '-U', 'postgres', '-c', 'create database nicedjango;'])

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASE_ENGINE=db_conf['ENGINE'],
        DATABASES={'default': db_conf},
        SITE_ID=1,
        SECRET_KEY='not very secret in tests',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',

            'nicedjango',
            'tests',
            'tests.a1',
            'tests.a2',
            'tests.a3',
            'tests.a4',
        ),
        LOGGING={'version': 1,
                 'handlers': {'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'}},
                 'loggers': {'django.db.backends': {'level': 'DEBUG', 'handlers': ['console']}}},
        DEBUG=True,
    )

    if hasattr(django, 'setup'):
        django.setup()

    # logging.basicConfig(level=logging.DEBUG)
    for level, color in ((logging.INFO, 32), (logging.WARNING, 33), (logging.ERROR, 31),
                         (logging.DEBUG, 34), (logging.CRITICAL, 35)):
        logging.addLevelName(level, "\033[1;%dm%s\033[1;m" % (color, logging.getLevelName(level)))
