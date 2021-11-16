from django.apps import AppConfig
from multi_tenant.tenant import get_all_tenant_db
from django.db import connections



class TenantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'multi_tenant.tenant'

    def ready(self) -> None:
        from .signal import create_data_handler
        from .patch.connection import ConnectionHandler
        from .patch.contenttype import management
        from .patch.permission import management
        from .patch.user import User
        dbs = list(get_all_tenant_db().keys())
        for db in dbs:
            connections[db]
        return super().ready()
