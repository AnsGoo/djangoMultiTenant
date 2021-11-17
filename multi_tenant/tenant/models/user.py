import unicodedata
from django.db import models
from django.utils.crypto import get_random_string
from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import (
    check_password, make_password,
)
from multi_tenant.tenant import get_common_apps, get_tenant_model, get_tenant_user_model



class BaseUserManager(models.Manager):

    def make_random_password(self, length:int=10,
                             allowed_chars:str='abcdefghjkmnpqrstuvwxyz'
                                           'ABCDEFGHJKLMNPQRSTUVWXYZ'
                                           '23456789') -> str:
        """
        Generate a random password with the given length and given
        allowed_chars. The default value of allowed_chars does not have "I" or
        "O" or letters and digits that look similar -- just to avoid confusion.
        """
        return get_random_string(length, allowed_chars)

    def get_by_natural_key(self, username:str) ->str:
        return self.get(**{self.model.USERNAME_FIELD: username})



class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username:str, password:str, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_super', True)
        return self._create_user(username, password, **extra_fields)

class AbstractGlobalUser(models.Model):
    Tenant = get_tenant_model()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_super = models.BooleanField(default=False)
    tenant = models.ForeignKey(Tenant,to_field='code',on_delete=models.CASCADE, null=True, blank=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']
    PASSWORD_FIELD = 'password'
    _password = None

    objects = UserManager()

    def __str__(self) -> str:
        return f'{self.username}'
    

    class Meta:
        verbose_name = '全局用户'
        verbose_name_plural = '全局用户'
        abstract = True

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_authenticated(self) -> bool:
        return True


    def get_username(self) -> bool:
        if hasattr(self,self.USERNAME_FIELD):
            return getattr(self, self.USERNAME_FIELD)
    @property
    def is_superuser(self) -> bool:
        return self.is_super


    @classmethod
    def normalize_username(cls, username:str):
        return unicodedata.normalize('NFKC', username) if isinstance(username, str) else username

    def check_password(self, raw_password:str):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    
    def set_password(self, raw_password:str):
        self.password = make_password(raw_password)
        self._password = raw_password

    def has_module_perms(self, app_label:str) -> bool:
        common_applist = get_common_apps()
        if self.tenant:
            if app_label in common_applist:
                return False
            else:
                return True
        else:
            if app_label in common_applist and self.is_super:
                return True
            else:
                return  False

    def has_perm(self, permission:str) -> bool:
        TenantUser = get_tenant_user_model()
        if self.tenant:
            try:
                tenant_user = TenantUser.objects.using(self.tenant.code).get(username=self.username)
                all_permissions = tenant_user.get_all_permissions()
                if permission in all_permissions:
                    result = tenant_user.has_perm(permission)
                    return result
                else:
                    return False
            except Exception as e:
                print(e)
                return False
        else:
            True

        return True


class GlobalUser(AbstractGlobalUser):
    pass