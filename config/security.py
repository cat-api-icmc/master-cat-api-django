from decouple import config as env

SECRET_KEY = env('SECRET_KEY')

PORT = env('PORT', default=8000, cast=int)

ALLOWED_PORTS = [PORT, 9443, 3000]

ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='*').split(';')

# --------------------------------------------- #

HOSTS = [f'{host}:{port}' for host in ALLOWED_HOSTS for port in ALLOWED_PORTS]

CSRF_TRUSTED_ORIGINS = [f'http://{host}' for host in HOSTS]

CORS_ORIGIN_WHITELIST = [f'http://{host}' for host in HOSTS]
    
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
