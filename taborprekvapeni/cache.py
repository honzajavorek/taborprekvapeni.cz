# -*- coding: utf-8 -*-


from hashlib import sha1
from functools import wraps

from flask import request, make_response
from werkzeug.contrib.cache import FileSystemCache, NullCache


class Cache(FileSystemCache):
    """Simple file system cache."""

    def __init__(self, app):
        super(Cache, self).__init__(
            app.config['CACHE_DIR'],
            default_timeout=app.config['CACHE_DEFAULT_TIMEOUT']
        )

    def cached_view(self, key='view/{request.path}', timeout=None):
        """View decorator."""
        timeout = timeout or self.default_timeout

        def decorator(f):
            @wraps(f)
            def decorated_view(*args, **kwargs):
                cache_key = key.format(request=request)

                response = self.get(cache_key)
                if response is not None:
                    return response.make_conditional(request)  # send HTTP 304

                rv = f(*args, **kwargs)
                response = make_response(rv)

                if isinstance(rv, unicode):  # ensure HTTP 304 for strings
                    response.set_etag(sha1(rv.encode('utf-8')).hexdigest())

                response.freeze()
                self.set(cache_key, response, timeout=timeout)

                return response
            return decorated_view
        return decorator

    def cached_call(self, key, call, timeout=None):
        timeout = timeout or self.default_timeout

        value = self.get(key)
        if value is not None:
            return value

        value = call()
        self.set(key, value)
        return value


class DevelopmentCache(NullCache):

    def __init__(self, app):
        pass

    def cached_view(self, *args, **kwargs):
        def decorator(f):
            return f
        return decorator

    def cached_call(self, key, call, *args, **kwargs):
        return call()
