# -*- coding: utf-8 -*-


import requests
import itertools
from requests import ConnectionError

from taborprekvapeni.cache import cache


headers = {'User-Agent': ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:19.0) '
                          'Gecko/20100101 Firefox/19.0')}


def get(url):
    """Get contents from remote URL as bytes. Caches results."""
    def request():
        def run():
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content

        for attempt in itertools.count():
            try:
                return run()
            except ConnectionError:  # unreliable Heroku
                if attempt > 5:
                    raise
                # else retry...

    return cache(url, request)
