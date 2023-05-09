from django.contrib.messages import constants as messages
from google.oauth2 import service_account
from pathlib import Path
from environs import Env
import os


env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")



# Application definition

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',     # for serving static files in production move this to top of list to have it run also in development
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # apps
    'pricing_app',
    'payments_app',
    'users_app',
    'shipping_app',
    'claims_app',
    # pip installed apps
    'debug_toolbar',
    'widget_tweaks',                    # for form customization
    'django_countries',
    'allauth',                          # for user authentication
    'allauth.account',                  # for user authentication
    'django_browser_reload',             # for live reloading
    'django_htmx',                       # small javascript library for ajax and html dom swapping
    'django_extensions', # for development
    'django_cleanup.apps.CleanupConfig', # this app should always be last
]

SITE_ID = 1
AUTHENTICATION_BACKENDS = (
'django.contrib.auth.backends.ModelBackend',
'allauth.account.auth_backends.AuthenticationBackend', # new
)

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'insuranceProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'insuranceProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases



AUTH_USER_MODEL = "users_app.CustomUser" 
# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'node_modules'),
    ]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]



# Base url to serve media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')



#################  Google Cloud storage  ##############
GOOGLE_JSON_FILE = "googleauth.json"
GS_BUCKET_NAME = "allinoneship_media_files"
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
# MEDIA_URL = "https://console.cloud.google.com/storage/browser/allinoneship_media_files/"
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    GOOGLE_JSON_FILE
)
#GS_BLOB_CHUNK_SIZE = 1024 * 256 * 40 # Needed for uploading large streams

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# API keys
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_API_VERSION = '2022-11-15'
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

# Session settings
CART_SESSION_ID = 'cart'

REALM_ID=env('REALM_ID')

# django-allauth settings
LOGIN_REDIRECT_URL = 'pricing_app:home'
ACCOUNT_LOGOUT_REDIRECT = 'pricing_app:home' 
ACCOUNT_SESSION_REMEMBER = True # this will remove the remember me checkbox on the login page, and just remember the user
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email' 
ACCOUNT_EMAIL_REQUIRED = True 
ACCOUNT_UNIQUE_EMAIL = True 




# Email server configuration
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # till the sendgrid is working output to console
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = env('SENDGRID_API_KEY')
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey' # Most bee => 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True



# HTTPS SETTINGS
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=2592000)  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")



# quickbooks
QB_REFRESH_TOKEN = env('QB_REFRESH_TOKEN')