from .base import *


DEBUG = False
WHITENOISE_MANIFEST_STRICT = False
ALLOWED_HOSTS = ''
BASE_URL = ''
REDIRECT_URI = ''

ADMIN = ''

DEFAULT_FROM_EMAIL = ''
DEFAULT_COSTUMER_SERVICE_EMAIL = ''
DEFAULT_DEV_EMAIL = ''
DEFAULT_DEV_EMAIL_2 = ''

SERVER_EMAIL = ''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("PROD_DATABASE_NAME"),
        'USER': env("PROD_DATABASE_USER"),
        'PASSWORD': env("PROD_DATABASE_PASSWORD"),
        'HOST': env("PROD_DATABASE_HOST"),
        'PORT': env("DATABASE_PORT"), 
        'CONN_MAX_AGE': None, 
    }
}