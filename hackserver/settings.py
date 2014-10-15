# Django settings for crimsononline project.

# FOR THE SITE TO WORK, YOU NEED TO CREATE A LOCAL SETTINGS FILE FIRST
# use `sample_local_settings.py` as a template

import os

DEBUG = True

TEMPLATE_DEBUG = DEBUG

_PROJECT_ROOT = os.environ.get('X_DJANGO_PROJECT_PATH', os.path.normpath(os.path.join(os.path.realpath(os.path.dirname(__file__)), '..')))
_APP_ROOT = os.path.normpath(os.path.join(_PROJECT_ROOT, '..', '..'))

TIME_ZONE = 'America/New_York'

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.harvardhackfest.com', ]

ROOT_URLCONF = 'hackserver.urls'

STATICFILES_DIRS = (
    os.path.join(_PROJECT_ROOT, "hackserver", "static"),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'hackserver.regconfirm',
)

try:
    from local_settings import *
except ImportError:
    pass

# Note: all code below this point is here for a reason - they depend on variables
#       being set in local_settings.py
