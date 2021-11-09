from django.contrib.admin import ModelAdmin


class TenantModelAdminMix:

    def has_module_permission(self, request):
        user  = request.user
        if user.is_authenticated and user.tenant:
            return super().has_module_permission(request)
        else:
            return False

class  SysModelAdminMix:

    def has_module_permission(self, request):
        user  = request.user
        if user.is_authenticated and not user.tenant:
            return True
        else:
            return False