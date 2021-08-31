import logging
from typing import Dict
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps as django_apps
from django.db.models import Model
from mult_tenant.const import DEFAULT_TENANT_MODEL
from django.conf import settings
logger = logging.getLogger('django.request')



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
    queryset  = Tenant.objects.using('default').filter(is_active=True)
    dbs = dict()
    for tenant in queryset:
        dbs[tenant.code] = tenant.get_db_config()
    return dbs