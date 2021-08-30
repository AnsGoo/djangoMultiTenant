from django.apps import AppConfig



class TenantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mult_tenant.tenant'

    def ready(self) -> None:
        from .signal import create_data_handler
        return super().ready()
