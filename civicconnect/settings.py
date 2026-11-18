import os
import sys
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from django.contrib.messages import constants as messages

try:
    from decouple import config, Csv
    _USE_DECOUPLE = True
except ImportError:
    _USE_DECOUPLE = False

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security-sensitive settings — read from environment / .env
# ---------------------------------------------------------------------------
IS_TESTING = 'test' in sys.argv

if _USE_DECOUPLE:
    DEBUG = config('DEBUG', default=False, cast=bool)
    if IS_TESTING:
        SECRET_KEY = os.environ.get('SECRET_KEY') or config('SECRET_KEY', default='django-insecure-test-throwaway-secret-key-1234567890') or 'django-insecure-test-throwaway-secret-key-1234567890'
    elif DEBUG:
        SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
    else:
        SECRET_KEY = config('SECRET_KEY', default='')
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost' if (DEBUG or IS_TESTING) else '', cast=Csv())
    _csrf_origins = config('CSRF_TRUSTED_ORIGINS', default='http://127.0.0.1:8000,http://localhost:8000' if DEBUG else '', cast=Csv())
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=(not DEBUG), cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=(not DEBUG), cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=(not DEBUG), cast=bool)
else:
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')
    if IS_TESTING:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-test-throwaway-secret-key-1234567890')
    elif DEBUG:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
    else:
        SECRET_KEY = os.environ.get('SECRET_KEY', '')
    _hosts = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost' if (DEBUG or IS_TESTING) else '')
    ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()]
    _csrf = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1:8000,http://localhost:8000' if DEBUG else '')
    _csrf_origins = [c.strip() for c in _csrf.split(',') if c.strip()]

    def _bool_from_env(key, default):
        val = os.environ.get(key)
        if val is None:
            return default
        return val.lower() in ('true', '1', 'yes')

    SECURE_SSL_REDIRECT = _bool_from_env('SECURE_SSL_REDIRECT', not DEBUG)
    SESSION_COOKIE_SECURE = _bool_from_env('SESSION_COOKIE_SECURE', not DEBUG)
    CSRF_COOKIE_SECURE = _bool_from_env('CSRF_COOKIE_SECURE', not DEBUG)

if not DEBUG and not IS_TESTING and not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY environment variable must be set in production when DEBUG=False.")

CSRF_TRUSTED_ORIGINS = [orig for orig in _csrf_origins if orig]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # CivicConnect Local Apps
    'accounts',
    'challenges',
    'solutions',
    'collaborations',
    'partnerships',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'civicconnect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.user_roles_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'civicconnect.wsgi.application'

# ---------------------------------------------------------------------------
# Database — supports DATABASE_URL for PostgreSQL on Render/Heroku
# ---------------------------------------------------------------------------
_database_url = os.environ.get('DATABASE_URL', '')
if _database_url:
    try:
        import dj_database_url
        DATABASES = {'default': dj_database_url.config(default=_database_url, conn_max_age=600)}
    except ImportError:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Fast hasher for testing to avoid 720k PBKDF2 iterations per test
if 'test' in sys.argv:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

# Password validation — minimum 8 characters
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Storages configuration (Django 4.2+ / 5.x / 6.x)
# In production, WhiteNoise compresses and creates hashed manifests for caching.
# In test environments, use standard StaticFilesStorage since collectstatic is not executed.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
            if 'test' in sys.argv
            else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        ),
    },
}

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'home'

# Email backend for development / password resets
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Bootstrap 5 Message Tags
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Production security settings — only active when DEBUG=False
# ---------------------------------------------------------------------------
if IS_TESTING:
    # Test runs: skip SECURE_SSL_REDIRECT, secure cookies and HSTS
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
elif not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
