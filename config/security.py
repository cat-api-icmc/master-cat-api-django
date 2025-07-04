from decouple import config as env

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['*']

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"
LOGIN_URL = "login"
