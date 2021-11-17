from django.http import Http404
from rest_framework import exceptions
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from multi_tenant.tenant import get_tenant_user_model

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

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


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """
    TenantUser = get_tenant_user_model()

    def has_permission(self, request, view):
        username = request.user.username
        current_user = None
        try:
            current_user = self.TenantUser.objects.filter(is_active=True).get(username=username)
        except self.TenantUser.DoesNotExist:
            return False
        
        return bool(current_user and current_user.is_staff)




class DjangoModelPermissions(BasePermission):
    """
    适配了djangoModelPermissions的多租户场景
    """
    TenantUser = get_tenant_user_model()
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    authenticated_users_only = True

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]

    def _queryset(self, view):
        assert hasattr(view, 'get_queryset') \
            or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, (
                '{}.get_queryset() returned None'.format(view.__class__.__name__)
            )
            return queryset
        return view.queryset

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        username = request.user.username
        current_user = None
        try:
            current_user = self.TenantUser.objects.filter(is_active=True).get(username=username)
        except self.TenantUser.DoesNotExist:
            return False
        
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user or (
           not request.user.is_authenticated and self.authenticated_users_only):
            return False

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)

        return current_user.has_perms(perms)


class DjangoModelPermissionsOrAnonReadOnly(DjangoModelPermissions):
    """
    Similar to DjangoModelPermissions, except that anonymous users are
    allowed read-only access.
    """
    authenticated_users_only = False


class DjangoObjectPermissions(DjangoModelPermissions):
    """
    适配了DjangoObjectPermissions的多租户场景
    """
    TenantUser = get_tenant_user_model()
    
    
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def get_required_object_permissions(self, method, model_cls):
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]

    def has_object_permission(self, request, view, obj):
        username = request.user.username
        current_user = None
        try:
            current_user = self.TenantUser.objects.filter(is_active=True).get(username=username)
        except self.TenantUser.DoesNotExist:
            return False
        # authentication checks have already executed via has_permission
        queryset = self._queryset(view)
        model_cls = queryset.model

        perms = self.get_required_object_permissions(request.method, model_cls)

        if not current_user.has_perms(perms, obj):
            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_object_permissions('GET', model_cls)
            if not current_user.has_perms(read_perms, obj):
                raise Http404

            # Has read permissions.
            return False

        return True

