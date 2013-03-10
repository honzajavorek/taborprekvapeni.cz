# -*- coding: utf-8 -*-


import logging
from hashlib import sha1
from flask import request
from functools import wraps
from urlparse import urlparse
from redis import StrictRedis, ConnectionPool

try:
    import cPickle as pickle
except ImportError:
    import pickle as pickle

from taborprekvapeni import app


def connect(app):
    url = urlparse(app.config['REDIS_URL'])
    max_connections = app.config['REDIS_MAX_CONNECTIONS']

    try:
        db = int(url.path.replace('/', ''))
    except (AttributeError, ValueError):
        db = 0

    pool = ConnectionPool(host=url.hostname, password=url.password, db=db,
                          port=url.port, max_connections=max_connections)
    return StrictRedis(connection_pool=pool)


redis = connect(app)


def cache(key, fn, exp=None, eternal=True):
    """Cache helper. Uses Redis.

    In case data are found in cache under *key*, they are
    immediately returned. If nothing is under *key*, *fn*
    is called to provide the data. Those are then stored
    to cache twice - once with expiration, once eternally.

    The eternal version of data is used in case an error
    occures during *fn* execution. That means, invalid or
    empty data should never be returned if the first cache
    miss ever was successful. No future irregular errors
    affect the eternal data. Exceptions are logged.
    """
    original_key = key
    key = sha1(original_key).hexdigest()
    key_eternal = key + '.eternal'

    # cache hit
    result = redis.get(key)
    if result:
        logging.debug('Cache hit (%s).', original_key)
        return pickle.loads(result)

    # cache miss
    try:
        logging.debug('Cache miss (%s).', original_key)
        result = fn()

    except:
        logging.exception('Cache fallback (%s) due:', original_key)
        if eternal:
            # fallback to eternal backup
            result = redis.get(key_eternal)
            return pickle.loads(result) if result else None

    # update cache
    if result:
        exp = exp or app.config['CACHE_EXPIRATION']
        pickled = pickle.dumps(result)

        redis.setex(key, exp, pickled)
        if eternal:
            redis.set(key_eternal, pickled)

    return result


def cached(exp=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not app.debug:
                return cache(request.path, lambda: f(*args, **kwargs),
                             exp=exp or app.config['CACHE_EXPIRATION'])
            else:
                return f(*args, **kwargs)
        return decorated_function
    return decorator
