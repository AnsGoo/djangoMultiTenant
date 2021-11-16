from typing import Dict, Any
from multi_tenant.tenant import get_tenant_model
from django.db.utils import load_backend
from django.db.models import Model
from django.conf import settings
from multi_tenant.local import get_current_db



class MutlTenantOriginConnection:
    
    Tenant = get_tenant_model()

    def create_connection(self, tentant:Tenant, popname: bool=False,**kwargs):
        engine = tentant.get_engine()
        backend = load_backend(engine)
        alias = tentant.code
        db_config = tentant.get_db_config()
        if popname:
            db_config.pop('NAME', None)
        db_config = { **db_config, **kwargs}
        conn = self.ensure_defaults(db_config)
        return backend.DatabaseWrapper(conn, alias)

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
    def db_for_read(self, model:Model, **hints) -> str:
        if model._meta.app_label in settings.DATABASE_APPS_MAPPING:
            return settings.DATABASE_APPS_MAPPING[model._meta.app_label]

        return get_current_db()

    def db_for_write(self, model:Model, **hints):
        if model._meta.app_label in settings.DATABASE_APPS_MAPPING:
            return settings.DATABASE_APPS_MAPPING[model._meta.app_label]

        return get_current_db()

    def allow_migrate(self, db:str, app_label:str, **hints) -> bool:
        if app_label == 'contenttypes':
            return True
        app_db = settings.DATABASE_APPS_MAPPING.get(app_label)
        if app_db == 'default' and db == 'default':
            return True
        elif app_db != 'default' and db != 'default':
            return True
        else:
            return False
