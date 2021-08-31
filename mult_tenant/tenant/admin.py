from typing import Any, Tuple
from mult_tenant.tenant.models import Tenant
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.backends import UserModel
from django.contrib.auth.admin import UserAdmin
from mult_tenant.tenant.utils.model import get_tenant_model
from django.db.models import Model
from django.http.request import HttpRequest


Tenant = get_tenant_model()

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display: Tuple = ('name', 'label', 'code', 'is_active')
    search_fields: Tuple = ('name', 'label', 'code')
    list_filter:Tuple = ('is_active', 'engine')
    def get_readonly_fields(self, request: HttpRequest, obj: Model=None) -> Tuple:
        if obj:
            return ("db_password",'db_name','engine', 'options') 
        return []

    def has_delete_permission(self, request: HttpRequest, obj: Model=None) -> bool:
    	# 禁用删除按钮
        return False

@admin.register(UserModel)
class MultTenancyUserAdmin(UserAdmin):


    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'tenant')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'tenant')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'tenant')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'tenant')

# admin.register(UserModel, MultTenancyUserAdmin)

