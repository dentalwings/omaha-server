# coding: utf8

from .settings import *

import os


class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

INSTALLED_APPS += (
    'django_nose',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--exe',
    '--with-coverage',
    '--cover-package=omaha_server,omaha,crash,feedback,sparkle,healthcheck,downloads',
    '--cover-inclusive',
    '--nologcapture',
    '-s',
]

MIGRATION_MODULES = DisableMigrations()
# Tricks to speed up Django tests

DEBUG = False
TEMPLATE_DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_db',
    }
}
SOUTH_TESTS_MIGRATE = False
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

REDIS_STAT_DB = os.environ.get('REDIS_STAT_DB', 13)

CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
}

CACHES['statistics'] = {
    'BACKEND': 'django_redis.cache.RedisCache',
    'LOCATION': 'redis://{REDIS_HOST}:{REDIS_PORT}:{REDIS_DB}'.format(
        REDIS_PORT=REDIS_STAT_PORT,
        REDIS_HOST=REDIS_STAT_HOST,
        REDIS_DB=REDIS_STAT_DB),
    'OPTIONS': {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    }
}


OMAHA_UID_KEY_PREFIX = 'test:uid'

CRASH_SYMBOLS_PATH = os.path.join(BASE_DIR, 'crash', 'tests', 'testdata', 'symbols')
CRASH_S3_MOUNT_PATH = os.path.join(BASE_DIR, 'crash', 'tests', 'testdata')

AWS_STORAGE_BUCKET_NAME = 'test'
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

SENTRY_STACKTRACE_DOMAIN = 'test'
SENTRY_STACKTRACE_ORG_SLUG = 'test'
SENTRY_STACKTRACE_PROJ_SLUG = 'test'
SENTRY_STACKTRACE_API_KEY = 'test'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

ALLOWED_HOSTS = [u'example.com']
