import environ
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['43.201.231.69', 'tukcappybo.xyz']
SITE_TITLE = "Web"


STATIC_ROOT = BASE_DIR / 'pybo/static/'
STATICFILES_DIRS = []


env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': '5432',
    }
}