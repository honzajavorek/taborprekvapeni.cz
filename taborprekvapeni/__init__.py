# -*- coding: utf-8 -*-


__version__ = '0.0.24'


import logging
from redis import StrictRedis as Redis

from flask import Flask


app = Flask(__name__)
app.config.from_object('taborprekvapeni.config')
logging.basicConfig(**app.config['LOGGING'])

redis = Redis.from_url(app.config['REDIS_URL'])


from taborprekvapeni import views, templating
