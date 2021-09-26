from django.contrib.auth.backends import ModelBackend, UserModel
from django.http.request import HttpRequest

from mult_tenant.utils.local import set_current_db

class MultTenantModelBackend(ModelBackend) :
    def authenticate(self, request:HttpRequest, username: str=None, password: str=None, **kwargs) -> UserModel:
        user = super().authenticate(request, username=username, password=password, **kwargs)
        print(user)
        if user and user.tenant:
            code = user.tenant.code
            set_current_db(code)
        return user
