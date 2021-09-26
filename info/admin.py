from django.contrib import admin

from info.models import User
from mult_tenant.tenant.middleware.admin import TenantModelAdminMix


@admin.register(User)
class UserAdmin(TenantModelAdminMix, admin.ModelAdmin):
    pass
# Register your models here.
