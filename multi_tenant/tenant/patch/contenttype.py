from django.apps import apps as global_apps
from django.conf import settings
from django.contrib.contenttypes import management
from django.contrib.contenttypes.management import get_contenttypes_and_models
from django.db import DEFAULT_DB_ALIAS

from multi_tenant.tenant import get_common_apps


def create_contenttypes(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    """
    Create content types for models in the given app.
    """
    if not app_config.models_module:
        return

    app_label = app_config.label
    try:
        app_config = apps.get_app_config(app_label)
        ContentType = apps.get_model('contenttypes', 'ContentType')
    except LookupError:
        return

    
    common_applist = get_common_apps()
    if app_config.name in common_applist:
        return None

    content_types, app_models = get_contenttypes_and_models(app_config, using, ContentType)
    if not app_models:
        return

    cts = [
        ContentType(
            app_label=app_label,
            model=model_name,
        )
        for (model_name, model) in app_models.items()
        if model_name not in content_types
    ]
    ContentType.objects.using(using).bulk_create(cts)
    if verbosity >= 2:
        for ct in cts:
            print("Adding content type '%s | %s'" % (ct.app_label, ct.model))

management.create_contenttypes = create_contenttypes