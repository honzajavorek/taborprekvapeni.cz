# -*- coding: utf-8 -*-


import os
import logging


MARKDOWN = {
    'extensions': ['headerid'],
    'output': 'html5',
}

LOGGING = {
    'format': '[%(asctime)s: %(levelname)s] %(message)s',
    'level': logging.DEBUG,
}

REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

HTTP_CACHE_EXPIRATION = 604800  # 1 week in seconds
