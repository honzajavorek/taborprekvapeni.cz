# -*- coding: utf-8 -*-


import logging
from redis import StrictRedis as Redis
from flask.ext.markdown import Markdown
from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object('taborprekvapeni.config')

logging.basicConfig(**app.config['LOGGING'])

redis = Redis.from_url(app.config['REDIS_URL'])
md = Markdown(app, **app.config['MARKDOWN'])


from taborprekvapeni.models import BasicInfo


@app.route('/')
def index():
    return render_template('index.html', info=BasicInfo())


@app.route('/informace-proc')
def brief_info():
    return render_template('brief_info.html')


@app.route('/kontakt-prihlaska')
def contact():
    return render_template('contact.html')


@app.route('/tym-vedoucich')
def team():
    return render_template('team.html')


@app.route('/historie-fotky')
def history():
    return render_template('history.html')


@app.route('/reference-zkusenosti')
def testimonials():
    return render_template('testimonials.html')


@app.route('/organizacni-informace')
def info():
    return render_template('info.html')
