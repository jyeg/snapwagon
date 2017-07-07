# Local imports.
from .base import *

__author__ = 'Jason Parent'

DEBUG = False

ALLOWED_HOSTS = ['snapwagon.io']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.abspath(os.path.join(BASE_DIR, '../../database/db.sqlite3')),
    }
}

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, '../../media'))

STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '../../static'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    merchant_id=BRAINTREE_MERCHANT_ID,
    public_key=BRAINTREE_PUBLIC_KEY,
    private_key=BRAINTREE_PRIVATE_KEY
)
