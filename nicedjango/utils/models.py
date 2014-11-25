from django.db import connections


def get_connection(model):
    return connections[model._default_manager.db]


def get_connection_name(connection):
    return connection.client.executable_name.lower()
