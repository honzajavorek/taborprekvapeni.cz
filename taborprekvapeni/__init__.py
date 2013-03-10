# -*- coding: utf-8 -*-


__version__ = '0.0.38'


import logging
from flask import Flask


app = Flask(__name__)
app.config.from_object('taborprekvapeni.config')
logging.basicConfig(**app.config['LOGGING'])


from taborprekvapeni import views, templating
