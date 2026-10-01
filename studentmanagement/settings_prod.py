"""
Production settings for studentmanagement project.
Import from settings.py is recommended, or override settings.py with this approach.
"""

import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings from Environment
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

# Remove empty credentials for SQLite
if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    DATABASES['default'].pop('USER', None)
    DATABASES['default'].pop('PASSWORD', None)
    DATABASES['default'].pop('HOST', None)
    DATABASES['default'].pop('PORT', None)

# Email Configuration from Environment
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@studentmanagement.edu')
SERVER_EMAIL = config('SERVER_EMAIL', default='noreply@studentmanagement.edu')

# Security Middleware and Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
    SECURE_CONTENT_SECURITY_POLICY = config('SECURE_CONTENT_SECURITY_POLICY', default=True, cast=bool)
    
    # Strict security headers
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# AWS S3 Configuration (Optional)
USE_S3 = config('USE_S3', default=False, cast=bool)
if USE_S3:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    
    # Use S3 for static and media files
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    STATIC_ROOT = 'static'
    MEDIA_ROOT = 'media'
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise for static files serving
WHITENOISE_ENABLED = config('WHITENOISE_ENABLED', default=True, cast=bool)
if WHITENOISE_ENABLED:
    MIDDLEWARE = [
        'whitenoise.middleware.WhiteNoiseMiddleware',
    ]
    # Already includes other middleware
    WHITENOISE_COMPRESS = True
    WHITENOISE_MAX_AGE = 86400

# Logging Configuration
LOG_LEVEL = config('LOG_LEVEL', default='INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'students': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# Session Configuration
SESSION_COOKIE_AGE = 604800  # 7 days
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Cache Configuration (Optional - Redis recommended for production)
CACHES = {
    'default': {
        'BACKEND': config('CACHE_BACKEND', default='django.core.cache.backends.locmem.LocMemCache'),
        'LOCATION': config('CACHE_LOCATION', default=''),
    }
}
