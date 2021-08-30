from mult_tenant.utils.local import set_current_db
from django.contrib.auth.middleware import AuthenticationMiddleware, RemoteUserMiddleware, PersistentRemoteUserMiddleware

class MultTenantAuthenticationMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        super().process_request(request)
        if hasattr(request,'user'):
            user = request.user
            if not user.is_anonymous and user.tenant:
                code = user.tenant.code
                set_current_db(code)


class MultTenantRemoteUserMiddleware(RemoteUserMiddleware):
    def process_request(self, request):
        super().process_request(request)
        if hasattr(request,'user'):
            user = request.user
            if not user.is_anonymous and user.tenant:
                code = user.tenant.code
                set_current_db(code)


class MultTenantPersistentRemoteUserMiddleware(PersistentRemoteUserMiddleware):
    force_logout_if_no_header = False
