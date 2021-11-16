"""
Creates permissions for all installed apps that need permissions.
"""

from django.apps import apps as global_apps
from django.contrib.contenttypes.management import create_contenttypes
from django.db import DEFAULT_DB_ALIAS, router
from django.contrib.auth.models import Permission
from django.contrib.auth.management import _get_all_permissions
from django.contrib.auth import management
from django.contrib.auth import backends
from django.conf import settings

from multi_tenant.tenant import get_common_apps


def create_permissions(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    if not app_config.models_module:
        return

    create_contenttypes(app_config, verbosity=verbosity, interactive=interactive, using=using, apps=apps, **kwargs)

    app_label = app_config.label
    try:
        app_config = apps.get_app_config(app_label)
        ContentType = apps.get_model('contenttypes', 'ContentType')
        Permission = apps.get_model('auth', 'Permission')
    except LookupError:
        return

    common_applist = get_common_apps()
    if app_config.name in common_applist:
        return

    if not router.allow_migrate_model(using, Permission):
        return

    # This will hold the permissions we're looking for as
    # (content_type, (codename, name))
    searched_perms = []
    # The codenames and ctypes that should exist.
    ctypes = set()

    for klass in app_config.get_models():
        # Force looking up the content types in the current database
        # before creating foreign keys to them.
        
        ctype = ContentType.objects.db_manager(using).get_for_model(klass, for_concrete_model=False)

        ctypes.add(ctype)
        for perm in _get_all_permissions(klass._meta):
            searched_perms.append((ctype, perm))

    # Find all the Permissions that have a content_type for a model we're
    # looking for.  We don't need to check for codenames since we already have
    # a list of the ones we're going to create.
    all_perms = set(Permission.objects.using(using).filter(
        content_type__in=ctypes,
    ).values_list(
        "content_type", "codename"
    ))

    perms = [
        Permission(codename=codename, name=name, content_type_id=ct.id)
        for ct, (codename, name) in searched_perms
        if (ct.pk, codename) not in all_perms
    ]
    Permission.objects.using(using).bulk_create(perms)
    if verbosity >= 2:
        for perm in perms:
            print("Adding permission '%s'" % perm)


def _get_group_permissions(self, user_obj):

    user_groups_field = user_obj._meta.get_field('groups')
    user_groups_query = 'group__%s' % user_groups_field.related_query_name()
    return Permission.objects.filter(**{user_groups_query: user_obj})


backends.ModelBackend._get_group_permissions = _get_group_permissions

management.create_permissions = create_permissions