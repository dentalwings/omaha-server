# coding: utf8

from django.utils import crypto
from .settings import *

DEBUG = False

ALLOWED_HOSTS = (os.environ.get('HOST_NAME'), '*')
SECRET_KEY = os.environ.get('SECRET_KEY') or crypto.get_random_string(50)

STATICFILES_STORAGE = 'omaha_server.s3utils.StaticS3Storage'
DEFAULT_FILE_STORAGE = 'omaha_server.s3utils.S3Storage'
PUBLIC_READ_FILE_STORAGE = 'omaha_server.s3utils.PublicReadS3Storage'

AWS_SES_REGION_NAME = os.environ.get('AWS_SES_REGION_NAME', 'us-west-1')
AWS_SES_REGION_ENDPOINT = os.environ.get(
    'AWS_SES_REGION_ENDPOINT', 'email.us-east-1.amazonaws.com'
)
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
S3_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME

EMAIL_BACKEND = 'django_ses.SESBackend'
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_RECIPIENTS = os.environ.get('EMAIL_RECIPIENTS')

STATIC_URL = ''.join([S3_URL, 'static/'])
AWS_PRELOAD_METADATA = True
AWS_IS_GZIPPED = True

FILEBEAT_HOST = os.environ.get('FILEBEAT_HOST', 'localhost')
FILEBEAT_PORT = os.environ.get('FILEBEAT_PORT', 9021)

CELERYD_HIJACK_ROOT_LOGGER = False

