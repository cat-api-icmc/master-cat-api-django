from decouple import config as env

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://cat.icmc.usp.br",
    "https://cat.icmc.usp.br:9447",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://cat.icmc.usp.br",
    "https://cat.icmc.usp.br:9447",
    "https://cat.icmc.usp.br:8447",
]

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"
LOGIN_URL = "login"
