DEFAULT_DB_ENGINE_MAP = {
    'oracle': 'django.db.backends.oracle',
    'mysql': 'django.db.backends.mysql',
    'sqlite3': 'django.db.backends.sqlite3',
    'postgres': 'django.db.backends.postgresql'
}

DEFAULT_TENANT_MODEL  = 'tenant.Tenant'
AUTH_TENANT_USER_MODEL = 'auth.User'