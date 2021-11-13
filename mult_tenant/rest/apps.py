from django.apps import AppConfig


class RestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mult_tenant.rest'
    
    def ready(self):
        from .patch import request
        return super().ready()
