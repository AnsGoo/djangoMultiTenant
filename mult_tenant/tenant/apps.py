from django.apps import AppConfig



class TenantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mult_tenant.tenant'

    def ready(self) -> None:
        from .signal import create_data_handler
        from mult_tenant.rest.patch.request import Request
        from mult_tenant.tenant.patch.connection import ConnectionHandler
        from mult_tenant.tenant.patch.contenttype import management
        from mult_tenant.tenant.patch.permission import management
        from mult_tenant.tenant.patch.user import User
        return super().ready()
