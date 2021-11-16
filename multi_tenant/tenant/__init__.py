import logging
from typing import Dict, List
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps as django_apps
from django.db.models import Model
from multi_tenant.const import DEFAULT_TENANT_MODEL, AUTH_TENANT_USER_MODEL
from django.conf import settings
logger = logging.getLogger('django.request')



def get_tenant_user_model() -> Model:
    """
    Return the User model that is active in this project.
    """
    try:
        default_tenant_model = settings.AUTH_TENANT_USER_MODEL
        if default_tenant_model:
            return django_apps.get_model(default_tenant_model, require_ready=False)
        else:
            return django_apps.get_model(AUTH_TENANT_USER_MODEL, require_ready=False)
    except ValueError:
        logger.error("DEFAULT_TENANT_MODEL must be of the form 'app_label.model_name'")
        raise ImproperlyConfigured("DEFAULT_TENANT_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        logger.error("DEFAULT_TENANT_MODEL refers to model '%s' that has not been installed" % settings.DEFAULT_TENANT_MODEL)
        raise ImproperlyConfigured(
            "DEFAULT_TENANT_MODEL refers to model '%s' that has not been installed" % settings.DEFAULT_TENANT_MODEL
        )

def get_tenant_model() -> Model:
    """
    Return the User model that is active in this project.
    """
    try:
        default_tenant_model = DEFAULT_TENANT_MODEL
        if settings.DEFAULT_TENANT_MODEL:
            default_tenant_model = settings.DEFAULT_TENANT_MODEL
        return django_apps.get_model(default_tenant_model, require_ready=False)
    except ValueError:
        logger.error("DEFAULT_TENANT_MODEL must be of the form 'app_label.model_name'")
        raise ImproperlyConfigured("DEFAULT_TENANT_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        logger.error("DEFAULT_TENANT_MODEL refers to model '%s' that has not been installed" % settings.DEFAULT_TENANT_MODEL)
        raise ImproperlyConfigured(
            "DEFAULT_TENANT_MODEL refers to model '%s' that has not been installed" % settings.DEFAULT_TENANT_MODEL
        )

def get_tenant_db(alias: str) -> Dict[str,str]:
    Tenant = get_tenant_model()
    try:
        tenant  = Tenant.objects.using('default').filter(is_active=True).get(code=alias)
        return tenant.get_db_config()
    except Tenant.DoesNotExist:
        logger.warning(f'db alias [{alias}] dont exists')
        pass


def get_all_tenant_db() -> Dict[str,Dict]:
    Tenant = get_tenant_model()
    dbs = dict()
    try:
        queryset  = Tenant.objects.using('default').filter(is_active=True)
        dbs = dict()
        for tenant in queryset:
            dbs[tenant.code] = tenant.get_db_config()
    except:
        pass
    return dbs

def get_common_apps() ->List[str]:
    common_applist = []
    for key, val  in settings.DATABASE_APPS_MAPPING.items():
        if val == 'default':
            common_applist.append(key)
    return common_applist