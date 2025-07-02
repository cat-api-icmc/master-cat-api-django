from django.utils.deprecation import MiddlewareMixin

from core.auth import TokenAuthentication


class AuthUserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            _user, _ = TokenAuthentication().authenticate(request)
            request._user = _user
        except:
            pass
