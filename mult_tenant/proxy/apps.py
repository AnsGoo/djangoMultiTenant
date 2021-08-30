from django.apps import AppConfig


class ProxyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mult_tenant.proxy'
