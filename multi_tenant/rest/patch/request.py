from rest_framework.request import Request
from rest_framework import exceptions

from multi_tenant.local import set_current_db


def __request_authenticate(self):
    """
    Attempt to authenticate the request using each authentication instance
    in turn.
    """
    for authenticator in self.authenticators:
        try:
            user_auth_tuple = authenticator.authenticate(self)
        except exceptions.APIException:
            self._not_authenticated()
            raise

        if user_auth_tuple is not None:
            self._authenticator = authenticator
            self.user, self.auth = user_auth_tuple
            if self.user and self.user.tenant:
                set_current_db(self.user.tenant.code)
            return

    self._not_authenticated()

Request._authenticate = __request_authenticate