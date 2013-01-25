# -*- coding: utf-8 -*-


import logging
from hashlib import sha1

try:
    import cPickle as pickle
except ImportError:
    import pickle as pickle

from taborprekvapeni import app, redis


def cache(key, fn):
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

    except Exception:
        logging.exception('Cache fallback (%s) due:', original_key)

        # fallback to eternal backup
        result = redis.get(key_eternal)
        return pickle.loads(result) if result else None

    # update cache
    exp = app.config['HTTP_CACHE_EXPIRATION']
    pickled = pickle.dumps(result)

    redis.setex(key, exp, pickled)
    redis.set(key_eternal, pickled)

    return result