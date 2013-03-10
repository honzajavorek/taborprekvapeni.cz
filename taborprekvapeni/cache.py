# -*- coding: utf-8 -*-


import times
import logging
import pymongo
from hashlib import sha1
from functools import wraps
from bson.binary import Binary
from flask import request, make_response

try:
    import cPickle as pickle
except ImportError:
    import pickle as pickle

from taborprekvapeni import app


mongo = pymongo.MongoClient(app.config['MONGO_URL'])
db = mongo[app.config['MONGO_DB']]

db.cache.ensure_index('at',
                      expire_after_seconds=app.config['CACHE_EXPIRATION'])


def cache(key, fn, exp=None):
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

    # cache hit
    result = db.cache.find_one({'_id': key})
    if result:
        logging.debug('Cache hit (%s).', original_key)
        return pickle.loads(result['val'])

    # cache miss
    try:
        logging.debug('Cache miss (%s).', original_key)
        result = fn()

    except:
        logging.exception('Cache fallback (%s) due:', original_key)

        # fallback to eternal backup
        result = db.eternal_cache.find_one({'_id': key})
        return pickle.loads(result['val']) if result else None

    # update cache
    if result:
        pickled = Binary(pickle.dumps(result))
        db.cache.insert({'_id': key, 'val': pickled, 'at': times.now()})
        db.eternal_cache.insert({'_id': key, 'val': pickled})

    return result


def cached(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not app.debug:
            content = cache(request.path, lambda: f(*args, **kwargs))
        else:
            content = f(*args, **kwargs)

        response = make_response(content)
        print repr(content)
        bytes = unicode(content).encode('utf-8')
        response.set_etag(sha1(bytes).hexdigest())
        response.make_conditional(request)
        return response

    return decorated_function
