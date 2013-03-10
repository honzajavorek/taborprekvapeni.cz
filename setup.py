# -*- coding: utf-8 -*-


import re
from setuptools import setup, find_packages


# determine version
code = open('taborprekvapeni/__init__.py', 'r').read(200)
version = re.search(r'__version__ = \'([^\'"]*)\'', code).group(1)


setup(
    name='taborprekvapeni',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'gunicorn==0.17.2',
        'gevent==0.13.8',
        'flask==0.9',
        'flask-markdown==0.3',
        'requests==1.1.0',
        'lxml>=3.1.beta1',
        'pymongo==2.4.2',
        'times==0.6',
        'pil==1.1.7',
        'unidecode==0.04.11',
        'flask-gzip==0.1',
    ],
)
