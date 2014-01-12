# -*- coding: utf-8 -*-


import os
from os import path

from flask import Flask

from .cache import Cache, DevelopmentCache


# config
DEBUG = bool(os.getenv('TABORPREKVAPENI_DEBUG', False))
MARKDOWN = {'extensions': ['headerid'], 'output': 'html5'}
CACHE_DEFAULT_TIMEOUT = 604800  # one week
CACHE_DIR = path.realpath(path.join(path.dirname(__file__), '..', 'tmp'))
GA_CODE = 'UA-1316071-16'


# application setup
app = Flask(__name__)
app.config.from_object(__name__)

cache = DevelopmentCache(app) if app.debug else Cache(app)


# views
from . import views, templating  # NOQA
