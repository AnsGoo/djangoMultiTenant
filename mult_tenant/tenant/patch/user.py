from django.core import checks
from django.db.models.query_utils import DeferredAttribute
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import AbstractUser, User
# from django.contrib.auth import get_user_model
from django.contrib.auth.checks import check_models_permissions, check_user_model
# from django.contrib.auth.signals import user_logged_in

from django.contrib.auth.apps import AuthConfig




class Meta(AbstractUser.Meta):
    swappable = 'AUTH_TENANT_USER_MODEL'


def ready(self):
    from django.contrib.auth.management import create_permissions
    post_migrate.connect(
        create_permissions,
        dispatch_uid="django.contrib.auth.management.create_permissions"
    )
    checks.register(check_user_model, checks.Tags.models)
    checks.register(check_models_permissions, checks.Tags.models)

User.Meta = Meta
AuthConfig.ready = ready

