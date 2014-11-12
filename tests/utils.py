from django.db.models.loading import get_app, get_models

from nicedjango.utils import model_label

APPNAMES = ('a1', 'a2', 'a3', 'a4')


def delete_all():
    for appname in APPNAMES:
        app = get_app(appname)
        for model in get_models(app):
            model.objects.all().delete()


def get_all_values():
    all_values = {}
    for appname in APPNAMES:
        for model in get_models(get_app(appname), include_auto_created=True):
            if not (model._meta.abstract or model._meta.proxy):
                model_values = list(model.objects.values())
                if model_values:
                    all_values[model_label(model)] = model_values
    return all_values
