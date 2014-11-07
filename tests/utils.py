from django.db.models.loading import get_app, get_models

APPNAMES = ('a1', 'a2', 'a3', 'a4')


def delete_all():
    for appname in APPNAMES:
        app = get_app(appname)
        for model in get_models(app):
            model.objects.all().delete()


def get_all_values():
    all_values = {}
    for appname in APPNAMES:
        app_values = {}
        for model in get_models(get_app(appname)):
            if not (model._meta.abstract or model._meta.proxy):
                model_values = list(model.objects.values())
                if model_values:
                    app_values[model.__name__.lower()] = model_values
        if app_values:
            all_values[appname] = app_values
    return all_values
