from decouple import config as env

SECRET_KEY = env('SECRET_KEY')

PORT = env('PORT', default=8000, cast=int)

ALLOWED_PORTS = [PORT, 3000]

# -- This shouldn't be configured host based -- #
# -- TODO: Improve this to be host agnostic --- #

FORCE_SCRIPT_NAME = env('FORCE_SCRIPT', default=None)

ALLOWED_HOSTS = [
    '127.0.0.1', 'localhost', 'cbt2.icmc.usp.br',
]

# --------------------------------------------- #

HOSTS = [f'{host}:{port}' for host in ALLOWED_HOSTS for port in ALLOWED_PORTS]

CSRF_TRUSTED_ORIGINS = [f'http://{host}' for host in HOSTS]

CORS_ORIGIN_WHITELIST = [f'http://{host}' for host in HOSTS]
    
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
