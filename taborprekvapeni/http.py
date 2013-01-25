# -*- coding: utf-8 -*-


import requests

from taborprekvapeni.cache import cache


def get(url):
    """Get contents from remote URL as bytes. Caches results."""
    def request():
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    return cache(url, request)
