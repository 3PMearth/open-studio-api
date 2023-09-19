"""
Django settings for studio_api project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from decouple import config, Csv
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = "static/"

STATICFILES_DIRS = (
    os.path.join('static/'),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY=config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

CURRENT_CONTRACT_ID_MUSIC = config('CURRENT_CONTRACT_ID_MUSIC', default=1, cast=int)
CURRENT_CONTRACT_ID_TICKET = config('CURRENT_CONTRACT_ID_TICKET', default=2, cast=int)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS',
                        default=['127.0.0.1','localhost'],
                        cast=Csv(str))
CSRF_TRUSTED_ORIGINS = config('DJANGO_CSRF_TRUSTED_ORIGINS', default=[], cast=Csv(str))


# Application definition

INSTALLED_APPS = [
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'drf_yasg',
    'storages', #for s3
    'corsheaders',
    "rest_framework",
    "rest_framework_api_key",
    "ebhealthcheck.apps.EBHealthCheckConfig",
    "users.apps.UsersConfig",
    "tokens.apps.TokensConfig",
    "contracts.apps.ContractsConfig",
    "payments.apps.PaymentsConfig",
    "orders.apps.OrdersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False

ROOT_URLCONF = "studio_api.urls"

SITE_ID = 1

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "studio_api.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config("DB_USER"),
        'PASSWORD': config("DB_PASSWORD"),
        'HOST': config("DB_HOST"),
        'PORT': config("DB_PORT"),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = False

SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      }
   }
}

SECURE_CROSS_ORIGIN_OPENER_POLICY=None

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage"
        },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_REGION = config('AWS_REGION')
AWS_STORAGE_BUCKET_NAME=config('AWS_STORAGE_BUCKET_NAME')
AWS_STORAGE_BASE_FOLDER_NAME=config('AWS_STORAGE_BASE_FOLDER_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (
    AWS_STORAGE_BUCKET_NAME, AWS_REGION)
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'

WEB3_PROVIDER_URL = config('WEB3_PROVIDER_URL')
PROXY_ADDRESS = config('PROXY_ADDRESS')
PROXY_PRIVATE_KEY = config('PROXY_PRIVATE_KEY')

PAYAPP_WEBHOOK_URL = config('PAYAPP_WEBHOOK_URL')



