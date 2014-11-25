import logging
import sys
from subprocess import call

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


def pytest_addoption(parser):
    parser.addoption("--db", action="store", choices=['sq', 'my', 'pg'], default='sq',
                     help="run with db")


def get_db_from_cmd_line_args():
    # if there is another way with pytest in pytest_configure to get it, this can vanish
    db = 'sq'
    is_this_one = False
    for arg in sys.argv:
        if is_this_one:
            if arg in ['sq', 'my', 'pg']:
                return arg
            return db
        if arg.startswith('--db'):
            if arg[5:] in ['sq', 'my', 'pg']:
                return arg[5:]
            is_this_one = True
    return db


def pytest_configure():
    db = get_db_from_cmd_line_args()
    db_conf = DBS[db]

    if db == 'my':
        call(['mysql', '-u', 'root', '-e', 'create database if not exists nicedjango;'])
    elif db == 'pg':
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
        ),
        LOGGING={'version': 1,
                 'handlers': {'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'}},
                 'loggers': {'django.db.backends': {'level': 'DEBUG', 'handlers': ['console']}}},
        DEBUG=True,
    )

    if hasattr(django, 'setup'):
        django.setup()

    logging.basicConfig(level=logging.DEBUG)
    for level, color in ((logging.INFO, 32), (logging.WARNING, 33), (logging.ERROR, 31),
                         (logging.DEBUG, 34), (logging.CRITICAL, 35)):
        logging.addLevelName(level, "\033[1;%dm%s\033[1;m" % (color, logging.getLevelName(level)))
