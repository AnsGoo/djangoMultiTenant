from typing import Dict, Any
from .model import get_tenant_model

from django.db.utils import load_backend
from django.conf import settings
from mult_tenant.utils.local import get_current_db

Tenant = get_tenant_model()

class MutlTenantOriginConnection:

    def create_connection(self, tentant:Tenant, popname: bool=False):
        engine = tentant.get_engine()
        backend = load_backend(engine)
        alias = tentant.code
        db_config = tentant.get_db_config()
        if popname:
            db_config.pop('NAME', None)
        self.ensure_defaults(db_config)
        return backend.DatabaseWrapper(db_config, alias)

    def ensure_defaults(self,conn: Dict) -> Dict[str,Any]:
        """
        Put the defaults into the settings dictionary for a given connection
        where no settings is provided.
        """
        conn.setdefault('ATOMIC_REQUESTS', False)
        conn.setdefault('AUTOCOMMIT', True)
        conn.setdefault('ENGINE', 'django.db.backends.dummy')
        if conn['ENGINE'] == 'django.db.backends.' or not conn['ENGINE']:
            conn['ENGINE'] = 'django.db.backends.dummy'
        conn.setdefault('CONN_MAX_AGE', 0)
        conn.setdefault('OPTIONS', {})
        conn.setdefault('TIME_ZONE', None)
        for setting in ['NAME', 'USER', 'PASSWORD', 'HOST', 'PORT']:
            conn.setdefault(setting, '')
        return conn


class MultTenantDBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label in settings.DATABASE_APPS_MAPPING:
            return settings.DATABASE_APPS_MAPPING[model._meta.app_label]

        return get_current_db()

    def db_for_write(self, model, **hints):
        if model._meta.app_label in settings.DATABASE_APPS_MAPPING:
            return settings.DATABASE_APPS_MAPPING[model._meta.app_label]

        return get_current_db()

    def allow_migrate(self, db, app_label, **hints):

        if app_label == 'contenttypes':
            return True
        app_db = settings.DATABASE_APPS_MAPPING.get(app_label)
        if app_db == 'default' and db == 'default':
            return True
        elif app_db != 'default' and db != 'default':
            return True
        else:
            return False
