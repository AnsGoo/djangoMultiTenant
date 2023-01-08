from multi_tenant.tenant import get_tenant_model
from django.db.utils import load_backend
from django.db.models import Model
from django.conf import settings
from multi_tenant.local import get_current_db
from django.db.utils import ConnectionHandler

class MutlTenantOriginConnection(ConnectionHandler):
    '''
    创建原始数据库连接
    '''
    
    Tenant = get_tenant_model()
    def create_connection(self, tentant:Tenant, popname: bool=False,**kwargs):
        '''
        根据租户信息创建原始数据库连接
        '''
        engine = tentant.get_engine()
        alias = tentant.code
        db_config = tentant.get_db_config()
        if popname:
            db_config['NAME'] = None
        conn = { **db_config, **kwargs}
        backend = load_backend(engine)
        return backend.DatabaseWrapper(conn, alias)


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
