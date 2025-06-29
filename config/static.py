from os import path
from decouple import config as env

BASE_DIR = path.dirname(path.dirname(__file__))

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

if env('DEBUG', default=False, cast=bool):
    MEDIA_ROOT = path.join(BASE_DIR, 'media')
    STATIC_ROOT = path.join(BASE_DIR, 'static')

    STATICFILES_DIRS = (
        path.join(BASE_DIR,  'core', 'assets'),
        path.join(BASE_DIR, 'core', 'media'),
    )
else:
    MEDIA_ROOT = path.join(BASE_DIR, 'core', 'media')
    STATIC_ROOT = path.join(BASE_DIR,  'core', 'assets')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [f'{BASE_DIR}/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
