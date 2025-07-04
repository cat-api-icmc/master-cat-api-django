from decouple import config as env

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://cat.icmc.usp.br",
    "https://cat.icmc.usp.br:9443",
]

CORS_ALLOW_ALL_ORIGINS = True

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"
LOGIN_URL = "login"
