from .base import *

DEBUG = env("DEBUG",False)

SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

try:
    from .local import *
except ImportError:
    pass
