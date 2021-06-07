from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1r+&l6bzfj&oi!p9t*^p!q1nq!yeg8th$2t4o=gr(gs*hltvpp'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CONSOLE_LOGGING_FORMAT = '%(asctime)s %(levelname)-8s %(name)s.%(funcName)s: %(message)s'
CONSOLE_LOGGING_FILE_LOCATION = os.path.join(BASE_DIR, 'django-eacw.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'my_formatter': {
            'format': CONSOLE_LOGGING_FORMAT,
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', ],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'my_formatter',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': CONSOLE_LOGGING_FILE_LOCATION,
            'mode': 'a',
            'encoding': 'utf-8',
            'formatter': 'my_formatter',
            'backupCount': 5,
            'maxBytes': 10485760,
        },
    },
    'loggers': {
        '': {
            # The root logger is always defined as an empty string and will pick up all logging that is not collected
            # by a more specific logger below
            'handlers': ['console', 'mail_admins', 'file'],
            'level': os.getenv('ROOT_LOG_LEVEL', 'INFO'),
        },
        'django': {
            # The 'django' logger is configured by Django out of the box. Here, it is reconfigured in order to
            # utilize the file logger and allow configuration at runtime
            'handlers': ['console', 'mail_admins', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.server': {
            'propagate': True,
        },
        'django.security.DisallowedHost': {
            'propagate': False,
            'level': 'ERROR',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}

try:
    from .local import *
except ImportError:
    pass
