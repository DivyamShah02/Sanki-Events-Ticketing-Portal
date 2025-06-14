import os
from pathlib import Path
from utils.encrypt_decrypt import *

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-o9!+or-a3a3g5@--zw%xcnv_m$1t2**ltd4g$7nm@n$elr!gwk'

DEBUG = True

ALLOWED_HOSTS = ['*']

X_FRAME_OPTIONS = 'SAMEORIGIN'

AUTH_USER_MODEL = 'UserDetail.User'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'FrontEnd',
    'UserDetail',
    'Event',
    'Ticket',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SankiEventsTicketPortal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, 'templates'],
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

WSGI_APPLICATION = 'SankiEventsTicketPortal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [
   os.path.join(BASE_DIR, 'static'),
]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')


# AWS S3 Configuration
AWS_ACCESS_KEY_ID = base64_to_text('QUtJQTVJSk9YQlFVVEVFNU9NSkI=')
AWS_SECRET_ACCESS_KEY = base64_to_text('TlIwblU5T0oyQ0lkQm1nRkFXMEk4RTRiT01na3NEVXVPQnJJTU5iNQ==')
AWS_STORAGE_BUCKET_NAME = 'sankievents'
AWS_S3_SIGNATURE_NAME = 's3v4'
AWS_S3_REGION_NAME = 'eu-north-1'
AWS_QUERYSTRING_AUTH = False


# S3 Media Files Configuration
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'

# Cache Control (Optional, for performance)
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
