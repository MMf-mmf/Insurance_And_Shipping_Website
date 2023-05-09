from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# OAauth2 config here
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://localhost:8000/payments/intuit_redirect'
ENVIRONMENT = 'sandbox'

BASE_URL = 'http://localhost:8000'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost','10.0.0.56', '192.168.0.231']
DEFAULT_FROM_EMAIL = '' 
DEFAULT_COSTUMER_SERVICE_EMAIL = ''
DEFAULT_DEV_EMAIL = ''
DEFAULT_DEV_EMAIL_2 = ''

NPM_BIN_PATH = "/Program Files/nodejs/npm.cmd" # for windows
#NPM_BIN_PATH = "/usr/local/bin/npm" # for mac
INTERNAL_IPS = [
    "127.0.0.1",
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DATABASE_NAME"),
        'USER': env("DATABASE_USER"),
        'PASSWORD': env("DATABASE_PASSWORD"),
    }
}

