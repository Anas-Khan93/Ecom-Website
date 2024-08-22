"""
Django settings for ai_interviewer project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
import environs
#import storages
from datetime import timedelta

from dotenv import load_dotenv
# load environment from the .env file
load_dotenv()

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_rest_passwordreset',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'ai_appinterviewer',
    'storages',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# REST_FRAMEWORK = {
#     "NON_FIELD_ERRORS_KEY": <desired key name>
# }


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ai_interviewer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ai_interviewer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Initialize environment variables
env= environs.Env()

# Read the .env file
environs.Env.read_env()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('MY_SECRET_KEY', default= 'Found no secret key')


DATABASES = {
    'default': env.db()
}

# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv("ENGINE", default=""),
#         'NAME': os.getenv("NAME", default=""),
#         'USER': os.getenv("USER", default=""),
#         'PASSWORD': os.getenv("PASSWORD", default=""),
#         'HOST' : os.getenv("HOST", default=""),
#         'PORT' : os.getenv("PORT", default=""),
#         'OPTIONS':{
            
#         },

#     },
# }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# AZURE STORAGE CODE PART:

# settings.py



# AZURE STORAGE CONFIGURATION

AZURE_CONTAINER = env("AZURE_CONTAINER")     # The name of your container
AZURE_CUSTOM_DOMAIN = f'{env("AZURE_ACCOUNT_NAME")}.blob.core.windows.net'


STORAGES = {
    "default": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "account_name": env("AZURE_ACCOUNT_NAME"),
            "account_key" : env("AZURE_ACCOUNT_KEY"),
            "azure_container": env("AZURE_CONTAINER"),
            "custom_domain": f'{env("AZURE_ACCOUNT_NAME")}.blob.core.windows.net' ,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfile.storage.StaticFileStorage",        
    },
}

#DEFAULT_FILE_STORAGE = 'ai_interviewer.custom_azure.AzureMediaStorage'
# AZURE_URL_EXPIRATION_SECS = None  # For public access, otherwise set expiration
MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/'


