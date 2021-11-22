from datetime import datetime
from typing import Dict, Tuple
from django.db import models
from multi_tenant.tenant.utils.pycrypt import crypt
from multi_tenant.const import DEFAULT_DB_ENGINE_MAP
from django.conf import settings


DAFAULT_DB = settings.DATABASES['default']


class TenantManager(models.Manager):
    def create_tenant(self, code, name,**kwargs):
        if not code:
            raise ValueError('The given code must be set')
        if not name:
            raise ValueError('The given name must be set')
        password = kwargs.pop('db_password',None)
        tenant = self.model(code=code, name=name, **kwargs)
        if password:
            tenant.db_password = crypt.encrypt(password)
        tenant.save(using=self._db)
        return tenant

class AbstractTenant(models.Model):
    Mysql, SQLite, Postgres, Oracle = ('Mysql', 'SQLite3', 'Postgres', 'Oracle')
    engine_choices = (
        (Mysql, Mysql),
        (SQLite, SQLite),
        (Postgres, Postgres),
        (Oracle, Oracle),
    )
    create_date: datetime = models.DateTimeField(auto_now_add=True)
    name: str = models.CharField(max_length=20, unique=True)
    label: str = models.CharField(max_length=200)
    code: str = models.CharField(max_length=10, unique=True)
    db_password: str = models.CharField(max_length=128, null=True, blank=True)
    db_name: str = models.CharField(max_length=50)
    engine: str = models.CharField(max_length=10, null=True, blank=True, choices=engine_choices)
    options: str = models.JSONField(null=True, blank=True)
    is_active: bool = models.BooleanField(default=True)
    _password = None
    CODE_FIED = 'code'
    objects = TenantManager()

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._password is not None:
            if self.db_password:
                raw_password = crypt.encrypt(self.db_password)
                self.db_password = raw_password
                self._password = None
                self.save()
    
    def delete(self, using: str=None, keep_parents: bool=False, force: bool = False) -> Tuple[int, Dict[str, int]]:
        if force:
            super().delete(using,keep_parents)
        else:
            raise PermissionError(f'{self.code} can not delete')
    
    def create_database(self) -> bool:
        from multi_tenant.tenant.utils.db import MutlTenantOriginConnection
        if self.engine.lower() == self.SQLite.lower():
            connection = MutlTenantOriginConnection().create_connection(tentant=self, popname=False)
            return True
        elif self.engine.lower() == self.Postgres.lower():
            connection = MutlTenantOriginConnection().create_connection(tentant=self, popname=True, **{'NAME':'postgres'})
        else:
            connection = MutlTenantOriginConnection().create_connection(tentant=self, popname=True)
            
        create_database_sql = self.create_database_sql
        if create_database_sql:
            with connection.cursor() as cursor:
                cursor.execute(create_database_sql)
        return True

    class Meta:
        db_table = 'auth_tenant'
        verbose_name = '租户'
        verbose_name_plural = '租户'
        abstract = True

    
    def get_db_config(self) -> Dict:
        if self.engine:
            engine_name = self.engine.lower()
        else:
            default_engine = DAFAULT_DB['ENGINE']
            engine_name = self.inject_engine(default_engine)
        if hasattr(self,f'_create_{engine_name}_dbconfig'):
            return getattr(self,f'_create_{engine_name}_dbconfig')()

        else:
            raise NotImplementedError(f'create_{engine_name}_dbconfig is not implemente')
    @staticmethod
    def inject_engine(name):
        for key ,value in DEFAULT_DB_ENGINE_MAP.items():
            if name == value:
                return key
    def _create_common_dbconfig(self) -> Dict:
        password = DAFAULT_DB['PASSWORD']
        engine = self.get_engine()
        options = self.options
        if not self.options:
            options = dict()

        if self.db_password:
            password = crypt.decrypt(self.db_password)
        return  {
                'ENGINE': engine,
                'NAME': self.db_name,
                'USER': options.pop('user', DAFAULT_DB['USER']),
                'PASSWORD': password,
                'HOST': options.pop('host', DAFAULT_DB['HOST']),
                'PORT': options.pop('port', DAFAULT_DB['PORT']),
                **options
            }
    

    def _create_sqlite3_dbconfig(self) -> Dict:
        engine = self.get_engine()

        return {
                'ENGINE': engine,
                'NAME': settings.BASE_DIR.joinpath(self.db_name)
            }


    def _create_mysql_dbconfig(self) -> Dict:
        return self._create_common_dbconfig()

    
    def _create_postgres_dbconfig(self) -> Dict:
        return self._create_common_dbconfig()

    def _create_oracle_dbconfig(self,) -> Dict:
        return self._create_common_dbconfig()


    def get_engine(self) -> str:
        engine = DAFAULT_DB['ENGINE']
        if self.engine:
            engine = DEFAULT_DB_ENGINE_MAP.get(self.engine.lower())
            if not engine:
                raise ValueError(f'unkown engine {self.engine}, engine must be in {list(DEFAULT_DB_ENGINE_MAP.keys())}')
        return engine
        
            
    @property
    def create_database_sql(self) -> str:
        engine_name = self.engine.lower()
        if hasattr(self,f'_create_{engine_name}_database'):
            return getattr(self,f'_create_{engine_name}_database')()
        else:
            raise NotImplementedError(f'_create_{engine_name}_database is not implemente')

    def _create_sqlite3_database(self) -> str:
        pass

    def _create_mysql_database(self) -> str:
        return f"CREATE DATABASE IF NOT EXISTS {self.db_name} character set utf8;"

    def _create_postgres_database(self) -> str:
        return f"CREATE DATABASE \"{self.db_name}\" encoding 'UTF8';"

    def _create_oracle_database(self) -> str:
  
        return f"CREATE DATABASE {self.db_name} DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
        
class Tenant(AbstractTenant):
    pass
    