from decouple import config as env

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = ["*"]

ALLOWED_ORIGINS = [
    "https://cat.icmc.usp.br",
    "https://cat.icmc.usp.br:9447",
]

CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS

CORS_ALLOWED_ORIGINS = ALLOWED_ORIGINS

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"
LOGIN_URL = "login"
