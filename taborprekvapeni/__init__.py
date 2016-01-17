# -*- coding: utf-8 -*-


import os
import logging
from os import path

from flask import Flask

from .cache import Cache, DevelopmentCache


# config
DEBUG = bool(os.getenv('TABORPREKVAPENI_DEBUG', False))
LOGGING = {'format': '[%(levelname)s] %(message)s', 'level': logging.DEBUG}
MARKDOWN = {'extensions': ['headerid'], 'output': 'html5'}
CACHE_DEFAULT_TIMEOUT = 604800  # one week
CACHE_DIR = path.realpath(path.join(path.dirname(__file__), '..', 'tmp'))
GA_CODE = 'UA-1316071-16'


# application setup
app = Flask(__name__)
app.config.from_object(__name__)


# logging
logging.basicConfig(**app.config['LOGGING'])

requests_log = logging.getLogger('requests')
requests_log.setLevel(logging.WARNING)


# cache
cache = DevelopmentCache(app) if app.debug else Cache(app)


# views
from . import views, templating  # NOQA
