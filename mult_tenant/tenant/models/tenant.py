from datetime import datetime
from typing import Dict, Tuple
from django.db import models
from mult_tenant.utils.pycrypt import crypt
from mult_tenant.const import DEFAULT_DB_ENGINE_MAP
from django.conf import settings


DAFAULT_DB = settings.DATABASES['default']


class AbstractTenant(models.Model):
    Mysql, SQLite, Posgrep, Oracle = ('Mysql', 'SQLite', 'Posgrep', 'Oracle')
    engine_choices = (
        (Mysql, Mysql),
        (SQLite, SQLite),
        (Posgrep, Posgrep),
        (Oracle, Oracle),
    )
    create_date: datetime = models.DateTimeField(auto_now_add=True)
    name: str = models.CharField(max_length=20, unique=True)
    label: str = models.CharField(max_length=200)
    code: str = models.CharField(max_length=10, unique=True)
    db_password: str = models.CharField(max_length=128,null=True, blank=True)
    db_name: str = models.CharField(max_length=50)
    engine: str = models.CharField(max_length=10, null=True, choices=engine_choices)
    options: str = models.JSONField(null=True, blank=True)
    is_active: bool = models.BooleanField(default=True)
    _password = None


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
    
    def delete(self, using: str, keep_parents: bool) -> Tuple[int, Dict[str, int]]:
        raise PermissionError(f'{self.code} can not delete')

    def create_database(self) -> bool:
        from mult_tenant.tenant.utils.db import MutlTenantOriginConnection
        if self.engine == self.SQLite:
            connection = MutlTenantOriginConnection().create_connection(tentant=self, popname=False)
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
        engine_name = self.engine.lower()
        if hasattr(self,f'create_{engine_name}_dbconfig'):
            return getattr(self,f'create_{engine_name}_dbconfig')()

        else:
            raise NotImplementedError(f'create_{engine_name}_dbconfig is not implemente')




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
    

    def create_sqlite3_dbconfig(self) -> Dict:
        engine = self.get_engine()

        return {
                'ENGINE': engine,
                'NAME': settings.BASE_DIR.joinpath(self.db_name)
            }


    def create_mysql_dbconfig(self) -> Dict:
        return self._create_common_dbconfig()

    
    def create_posgrep_dbconfig(self) -> Dict:
        return self._create_common_dbconfig()

    def create_oracle_dbconfig(self,) -> Dict:
        return self._create_common_dbconfig()


    def get_engine(self) -> str:
        engine = DAFAULT_DB['ENGINE']
        if self.engine:
            engine = DEFAULT_DB_ENGINE_MAP.get(self.engine.lower())
            if not engine:
                raise ValueError(f'unkown engine {self.engine}, engine must be in f{list(DEFAULT_DB_ENGINE_MAP.keys())}')
        return engine
        
            
    @property
    def create_database_sql(self) -> str:
        engine_name = self.engine.lower()
        if hasattr(self,f'create_{engine_name}_database'):
            return getattr(self,f'create_{engine_name}_database')()
        else:
            raise NotImplementedError(f'create_{engine_name}_database is not implemente')

    def create_sqlite3_database(self) -> str:
        pass

    def create_mysql_database(self) -> str:
        return f"CREATE DATABASE IF NOT EXISTS {self.db_name} character set utf8;"

    def create_posgrep_database(self) -> str:
        return f"CREATE DATABASE IF NOT EXISTS {self.db_name} character set utf8;"

    def create_oracle_database(self) -> str:
        return f"CREATE DATABASE IF NOT EXISTS {self.db_name} character set utf8;"
        
class Tenant(AbstractTenant):
    pass
    