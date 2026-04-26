"""
AkwabaFoncier — settings_production.py
Pour utiliser en production : 
  export DJANGO_SETTINGS_MODULE=akwabafoncier.settings_production
"""
from .settings import *
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='akwabafoncier_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD',default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER', default='octogone.techs@gmail.com')

# Paiements
CINETPAY_API_KEY = config('CINETPAY_API_KEY', default='')
CINETPAY_SITE_ID = config('CINETPAY_SITE_ID', default='')
CINETPAY_NOTIFY_URL = config('CINETPAY_NOTIFY_URL', default='')
CINETPAY_RETURN_URL = config('CINETPAY_RETURN_URL', default='')

# Sécurité HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# WhiteNoise (déjà dans settings.py, juste confirmation)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
