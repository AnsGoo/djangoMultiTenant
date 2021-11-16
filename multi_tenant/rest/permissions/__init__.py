from rest_framework.permissions import BasePermission
from rest_framework.request import Request

class IsTanenatUser(BasePermission):
    """
    超级用户默认拥有所有权限，如果是租户用户，公司编码不能为空，
    """
    def has_permission(self, request: Request, view) -> bool:
        user = request.user
        if user.is_authenticated and user.tenant:
            return bool(request.user.tenant)
        else:
            return False
