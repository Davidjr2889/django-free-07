import datetime
import os
from os import environ

from celery.schedules import crontab
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


def get_env_setting(setting):
    try:
        return environ[setting]
    except KeyError:
        raise ImproperlyConfigured(f"Falta definir e variável de ambiente: {setting}")

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = get_env_setting("SECRET_KEY")

DEBUG = True
INTERNAL_IPS = ('127.0.0.1',)
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]
ADMINS = (('Pedro Beck', 'pbeck@10.digital'),)
MANAGERS = ADMINS

# Application definition

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
)

THIRD_PARTY_APPS = (
    "rest_framework",
    "rest_framework_swagger",
    "debug_toolbar",
    "corsheaders",
    "nested_admin"
)

LOCAL_APPS = (
    "backoffice",
    # "sap",
    "prev_log"
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)


ROOT_URLCONF = 'LBARM.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'LBARM.wsgi.application'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1209600  # (2 weeks, in seconds)

# ----------------
# EMAIL
# ----------------

SERVER_EMAIL = "lbarm@licorbeirao.com"
DEFAULT_FROM_EMAIL = SERVER_EMAIL
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = get_env_setting("EMAIL_HOST")
EMAIL_HOST_USER = get_env_setting("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_env_setting("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = u"[LBARM] "

# ----------------
# DATABASE
# ----------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "lbarm_criasol",
        "USER": get_env_setting("DEFAULT_DATABASE_USER"),
        "PASSWORD": get_env_setting("DEFAULT_DATABASE_PASS"),
        "HOST": get_env_setting("DEFAULT_DATABASE_HOST"),
        "PORT": get_env_setting("DEFAULT_DATABASE_PORT"),
        "ATOMIC_REQUESTS": True,
    },
}

# ----------------
# CACHE
# ----------------

if DEBUG:
    CACHES = {
        "default": {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake'
        },
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'pt-pt'

LOCALE_PATHS = (
    # os.path.join(BASE_DIR, "locale"),
    os.path.join(os.path.dirname(BASE_DIR), "django-jwt-auth/locale"),
)

TIME_ZONE = 'Europe/Lisbon'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/djstatic/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'site_media')
MEDIA_URL = '/site_media/'

# -----------------
# DJANGO-SWAGGER
# -----------------

SWAGGER_SETTINGS = {
    "exclude_namespaces": [],  # List URL namespaces to ignore
    "api_version": '0.1',  # Specify your API's version
    "api_path": "/",  # Specify the path to your API not a root level
    "enabled_methods": [  # Specify which methods to enable in Swagger UI
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    "api_key": '',  # An API key
    "is_authenticated": True,  # Set to True to enforce user authentication,
    "is_superuser": True,  # Set to True to enforce admin only access
}
USE_SESSION_AUTH = True
LOGOUT_URL = "/accounts/logout/"


# ----------------------
# DJANGO REST FRAMEWORK
# ----------------------

REST_FRAMEWORK = {
    'FORM_METHOD_OVERRIDE': None,
    'FORM_CONTENT_OVERRIDE': None,

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        # 'api.authentication.DRFJWTAuthentication'
    )
}

# --------------------
# Django cors headers
# --------------------

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    "null",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:8048",
    "http://10.0.0.225",
    "http://backoffice.licorbeirao.com"
)
CSRF_TRUSTED_ORIGINS = (
    "null",
    "localhost:8000",
    "localhost:8080",
    "localhost:8048",
    "10.0.0.225",
    "backoffice.licorbeirao.com"
)
CORS_ALLOW_CREDENTIALS = True

# ----------------
# JWT
# ----------------

JWT_EXPIRATION_DELTA = datetime.timedelta(days=7)
JWT_ALLOW_REFRESH = True
JWT_REFRESH_EXPIRATION_DELTA = datetime.timedelta(days=20)
JWT_AUDIENCE = "backoffice.licorbeirao.com"
JWT_ISSUER = "Licor Beirão"
JWT_AUTH_COOKIE = "jwt_token"

# ----------------
# CELERY
# ----------------

# CELERY_IMPORTS = (
# )

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BROKER_URL = "redis://localhost:6379/1"

CELERY_RESULT_BACKEND = 'django-db'
# CELERY_BEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

CELERY_WORKER_DISABLE_RATE_LIMITS = True
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_TASK_ERROR_WHITELIST = ()

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Europe/Lisbon'

CELERY_TASK_RESULT_EXPIRES = 7 * 24 * 3600
CELERY_RESULT_EXPIRES = 7 * 24 * 3600


if DEBUG:
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

# CELERY_TASK_IGNORE_RESULT = True
# CELERY_WORKER_REDIRECT_STDOUTS_LEVEL = "DEBUG"
# CELERYD_LOG_LEVEL = "INFO"

CELERY_BEAT_SCHEDULE = {

}
