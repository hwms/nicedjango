from __future__ import unicode_literals

from django.core.files.temp import NamedTemporaryFile
from django.db import transaction
from django.utils.encoding import smart_text

from nicedjango.utils.compact_csv import quote_value
from nicedjango.utils.fields import (db_prep_values_list, get_fields_dict, get_pk_name,
                                     get_quoted_columns)
from nicedjango.utils.models import get_connection, get_connection_name
from nicedjango.utils.py.chunk import as_chunks
from nicedjango.utils.py.collections import get_or_create
from nicedjango.utils.py.iter import index_shift_map
from nicedjango.utils.queries import partition_existing_pks

__all__ = ['BulkCreator', 'bulk_replace_values', 'bulk_update_values', 'reset_tables']

_CACHE = {}


def get_bulk_creator(model, names, chunksize=None):
    return get_or_create(_CACHE, (model, tuple(names), chunksize),
                         BulkCreator, model, names, chunksize)


def bulk_replace_values(values_list, model, names, chunksize=None):
    names = tuple(names)
    get_bulk_creator(model, names, chunksize).replace(values_list)


def bulk_update_values(values_list, model, names, chunksize=None):
    names = tuple(names)
    get_bulk_creator(model, names, chunksize).update(values_list)


def reset_tables(model):
    get_bulk_creator(model, (get_pk_name(model),)).reset_tables()


class BulkCreator(object):

    def __init__(self, model, names, chunksize):
        self.model = model
        self.names = names
        self.chunksize = chunksize
        self.manager = model._default_manager
        self.pk_name = get_pk_name(model)
        self.pk_index = names.index(self.pk_name)
        self.table = model._meta.db_table
        self.connection = get_connection(model)
        self.connection_name = get_connection_name(self.connection)
        self.is_pgsql = 'psql' in self.connection_name
        self.is_mysql = 'mysql' in self.connection_name

        self.fields_dict = get_fields_dict(model, names)
        self.fields = self.fields_dict.values()
        self.columns = get_quoted_columns(self.connection, self.fields)

    def replace(self, values_list):
        if self.is_mysql:
            self.replace_into_mysql(values_list)
        else:
            to_create, to_update = partition_existing_pks(self.model, self.pk_index, values_list)
            self.update(list(to_update))
            self.insert_into(list(to_create))

    def update(self, values_list):
        if not values_list:
            return
        query_string = self.get_update_querystring()
        prep_list = list(db_prep_values_list(self.fields, self.connection, values_list))
        parameters = list(index_shift_map(self.pk_index, -1, prep_list))
        self.connection.cursor().executemany(query_string, parameters)
        transaction.commit_unless_managed(self.manager.db)

    def get_update_querystring(self):
        values = list(map(lambda c: '%s=%%s' % c, self.columns))
        where = values.pop(self.pk_index)
        values = ', '.join(values)
        return 'UPDATE %s SET %s WHERE %s' % (self.table, values, where)

    def get_into_querystring(self, command):
        columns = ', '.join(self.columns)
        values = ', '.join(('%s',) * len(self.columns))
        return '%s INTO %s (%s) VALUES (%s)' % (command, self.table, columns, values)

    def insert_into(self, values_list):
        self._sql_into('INSERT', values_list)

    def replace_into(self, values_list):
        self._sql_into('REPLACE', values_list)

    def _sql_into(self, command, values_list):
        if not values_list:
            return
        query_string = self.get_into_querystring(command)
        prep_list = list(db_prep_values_list(self.fields, self.connection,
                                             values_list))
        cursor = self.connection.cursor()
        cursor.executemany(query_string, prep_list)
        transaction.commit_unless_managed(self.manager.db)

    def replace_into_mysql(self, values_list):
        for chunk in as_chunks(values_list, self.chunksize):
            lines = []
            for row in chunk:
                lines.append(('%s\n' % smart_text(','.join(map(quote_value, row)))).encode('utf-8'))
            self.replace_into_mysql_lines(lines)

    def replace_into_mysql_lines(self, lines):
        with NamedTemporaryFile() as tmp_file:
            tmp_file.writelines(lines)
            tmp_file.flush()
            cursor = self.connection.cursor()
            columns = ','.join(self.columns)
            try:
                cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
                cursor.execute("LOAD DATA LOCAL INFILE '%s' "
                               "REPLACE INTO TABLE %s "
                               "FIELDS TERMINATED BY ',' "
                               "OPTIONALLY ENCLOSED BY '\"' "
                               "ESCAPED BY '\\\\' (%s)"
                               % (tmp_file.name, self.table, columns))
            finally:
                cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
            transaction.commit_unless_managed(self.manager.db)

    def reset_tables(self):
        self.manager.all().delete()
        if self.is_mysql:
            cursor = self.connection.cursor()
            cursor.execute('ALTER TABLE %s AUTO_INCREMENT = 1' % self.table)
        if self.is_pgsql:
            cursor = self.connection.cursor()
            cursor.execute("SELECT pg_get_serial_sequence('%s', '%s')"
                           % (self.table, self.model._meta.pk.column))
            seq_name = list(cursor)[0][0]
            if seq_name:
                cursor.execute("ALTER SEQUENCE %s RESTART WITH 1" % seq_name)
        transaction.commit_unless_managed(self.manager.db)
