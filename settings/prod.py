# Local imports.
from .base import *

__author__ = 'Jason Parent'

DEBUG = False

ALLOWED_HOSTS = ['snapwagon.io', '*.snapwagon.io', 'staging.snapwagon.io', '*.staging.snapwagon.io']

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

stripe.api_key = STRIPE_API_KEY
