DEFAULT_DB_ENGINE_MAP = {
    'oracle': 'django.db.backends.oracle',
    'mysql': 'django.db.backends.mysql',
    'sqlite3': 'django.db.backends.sqlite3',
    'posgrep': 'django.db.backends.postgresql_psycopg2'
}

DEFAULT_TENANT_MODEL  = 'tenant.Tenant'