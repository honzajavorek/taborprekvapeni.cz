# -*- coding: utf-8 -*-


import os
import logging


MARKDOWN = {
    'extensions': ['headerid'],
    'output': 'html5',
}

LOGGING = {
    'format': '[%(levelname)s] %(message)s',
    'level': logging.DEBUG,
}

REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
REDIS_MAX_CONNECTIONS = 10

CACHE_EXPIRATION = 604800  # 1 week in seconds
SEND_FILE_MAX_AGE_DEFAULT = 157680000  # 5 years in seconds

GA_CODE = 'UA-1316071-16'
