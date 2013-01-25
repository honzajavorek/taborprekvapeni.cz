# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


setup(
    name='taborprekvapeni',
    version='0.0.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'gunicorn==0.17.2',
        'gevent==0.13.8',
        'flask==0.9',
        'flask-markdown==0.3',
        'requests==1.1.0',
        'lxml>=3.1.beta1',
        'redis==2.7.2',
        'times==0.6',
    ],
)
