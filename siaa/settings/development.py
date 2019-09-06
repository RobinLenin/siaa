from .base import *
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'http://localhost/media/'
LDAP_ACTIVE = False
DEBUG = True
ALLOWED_HOSTS = []
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': '-c search_path=django,public'
        },
        'NAME': 'siaaf',
        'USER': 'siaaf',
        'PASSWORD': 'siaaf',
        'HOST': 'localhost',
        'PORT': '5432',

    },

    'bsg': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': '-c search_path=bsg,public'
        },
        'NAME': 'siaaf',
        'USER': 'siaaf',
        'PASSWORD': 'siaaf',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# celery
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = "America/Guayaquil"