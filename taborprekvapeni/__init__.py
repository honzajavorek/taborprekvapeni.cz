# -*- coding: utf-8 -*-


__version__ = '0.0.33'


import logging
from redis import StrictRedis as Redis, ConnectionPool as RedisPool

from flask import Flask


app = Flask(__name__)
app.config.from_object('taborprekvapeni.config')
logging.basicConfig(**app.config['LOGGING'])

redis_pool = RedisPool(max_connections=app.config['REDIS_MAX_CONNECTIONS'])
redis = Redis.from_url(app.config['REDIS_URL'],
                       connection_pool=redis_pool)


from taborprekvapeni import views, templating
