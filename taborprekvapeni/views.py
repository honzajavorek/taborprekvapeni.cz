# -*- coding: utf-8 -*-

import times
from flask import render_template

from taborprekvapeni import app
from taborprekvapeni.models import BasicInfo


@app.context_processor
def inject_info():
    info = BasicInfo()

    now = times.to_local(times.now(), 'Europe/Prague')
    camp_date = info['senior']['ends_at']

    return {
        'info': info,
        'volume': camp_date.year - 1997,
        'is_past': now.date() > camp_date,
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/informace')
def info():
    return render_template('info.html')


@app.route('/kontakt-prihlaska')
def contact():
    return render_template('contact.html')


@app.route('/tym-vedoucich')
def team():
    return render_template('team.html')


@app.route('/historie-fotky')
def history():
    return render_template('history.html')
