# import environ
from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = ["43.201.231.69", "tukcappybo.xyz"]

# SITE_TITLE = "Web"
SITE_TITLE = "CRIMO"


"""
STATIC_ROOT = BASE_DIR / 'pybo/static/'
"""
STATICFILES_DIRS = []


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static/"


DB_ENGINE = "sqlite"

if DB_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db" / "db.sqlite3",
        }
    }


"""
elif DB_ENGINE == "postgresql":
    env = environ.Env()
    environ.Env.read_env(BASE_DIR / ".env")

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST"),
            "PORT": "5432",
        }
    }
"""
