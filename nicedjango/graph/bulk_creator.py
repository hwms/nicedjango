from itertools import chain
from operator import itemgetter

from django.db import connections

__all__ = ['BulkValuesListCreator']


class BulkValuesListCreator(object):

    def __init__(self, model, fields):
        self.pk_field = model._meta.pk
        if self.pk_field not in fields:
            raise ValueError('pk field %s not in fields %s' % (self.pk_field,
                                                               fields))
        self.pk_index = fields.index(self.pk_field)
        self.model = model
        self.table = model._meta.db_table
        self.using = getattr(model, 'using', 'default')
        self.connection = connections[self.using]

        self.fields = fields
        self.columns = []
        for field in fields:
            self.columns.append(self.connection.ops.quote_name(field.column))
        self.pk_index = fields.index(model._meta.pk)

    def update_or_create(self, values_list):
        if 'mysql' in self.connection.client.executable_name.lower():
            self._mysql_replace_into(values_list)
        else:
            old_pks = self.get_existing_pks(values_list)
            to_update, to_create = self._split_by_pks(values_list, old_pks)
            self._update_many(to_update)
            self._insert_into(to_create)

        # transaction.commit_unless_managed(using=self.using)

    def _split_by_pks(self, values_list, pks):
        in_list = []
        not_in_list = []
        for values in values_list:
            if values[self.pk_index] in pks:
                in_list.append(values)
            else:
                not_in_list.append(values)
        return in_list, not_in_list

    def _db_prep(self, values_list):
        prepared_list = []
        for values in values_list:
            prepared = []
            for field, value in zip(self.fields, values):
                prepared.append(field.get_db_prep_save(value, self.connection))
            prepared_list.append(prepared)
        return prepared_list

    def get_existing_pks(self, values_list):
        pks = map(itemgetter(self.pk_index), values_list)
        filters = {'%s__in' % self.pk_field.name: pks}
        return set(self.model._default_manager.filter(**filters)
                                              .values_list(self.pk_field.name,
                                                           flat=True))

    def _update_many(self, values_list):
        if not values_list:
            return
        value_strings = list(map(lambda c: '%s=%%s' % c, self.columns))
        where_string = value_strings.pop(self.pk_index)
        value_string = ', '.join(value_strings)
        query_string = 'UPDATE %s SET %s WHERE %s' % (self.table, value_string,
                                                      where_string)
        prep_list = self._db_prep(values_list)
        parameters = list(self._iter_with_pk_last(prep_list))
        self.connection.cursor().executemany(query_string, parameters)

    def _iter_with_pk_last(self, values_list):
        for values in values_list:
            yield self._values_with_pk_last(values)

    def _values_with_pk_last(self, values):
        values = list(values)
        values.append(values.pop(self.pk_index))
        return values

    def _insert_into(self, values_list):
        self._sql_into('INSERT', values_list)

    def _mysql_replace_into(self, values_list):
        self._sql_into('REPLACE', values_list)

    def _sql_into(self, sql_command, values_list):
        if not values_list:
            return
        values_string = '(%s)' % ', '.join(('%s',) * len(self.fields))
        values_strings = (values_string,) * len(values_list)
        query_string = ('%s INTO %s (%s) VALUES %s'
                        % (sql_command, self.table, ', '.join(self.columns),
                           ', '.join(values_strings)))
        prep_list = self._db_prep(values_list)
        self.connection.cursor().execute(query_string,
                                         list(chain.from_iterable(prep_list)))
