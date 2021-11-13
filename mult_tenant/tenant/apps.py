from django.apps import AppConfig



class TenantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mult_tenant.tenant'

    def ready(self) -> None:
        from .signal import create_data_handler
        from .patch.connection import ConnectionHandler
        from .patch.contenttype import management
        from .patch.permission import management
        from .patch.user import User
        return super().ready()
