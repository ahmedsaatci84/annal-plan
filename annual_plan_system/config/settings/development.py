from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# MySQL database — credentials loaded from .env via base.py DATABASES config

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
