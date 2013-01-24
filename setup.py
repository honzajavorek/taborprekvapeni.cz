# -*- coding: utf-8 -*-


from datetime import datetime
from setuptools import setup, find_packages


setup(
    name='taborprekvapeni',
    version=datetime.utcnow().strftime('%Y.%m.%d'),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'gunicorn==0.17.2',
        'gevent==0.13.8',
        'flask==0.9',
    ],
)
