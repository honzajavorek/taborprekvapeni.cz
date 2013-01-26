# -*- coding: utf-8 -*-

import times
from flask import render_template, abort

from taborprekvapeni import app
from taborprekvapeni.cache import cached
from taborprekvapeni.models import BasicInfo, HistoryText


@app.context_processor
def inject_info():
    info = BasicInfo()

    now = times.to_local(times.now(), 'Europe/Prague')
    camp_date = info['senior']['ends_at']

    return {
        'info': info,
        'volume_year': camp_date.year,
        'volume_no': camp_date.year - 1997,
        'is_past': now.date() > camp_date,
    }


@app.route('/')
@cached()
def index():
    return render_template('index.html')


@app.route('/informace')
@cached()
def info():
    return render_template('info.html')


@app.route('/kontakt-prihlaska')
@cached()
def contact():
    return render_template('contact.html')


@app.route('/tym-vedoucich')
@cached()
def team():
    return render_template('team.html')


@app.route('/historie-fotky/<int:year>')
@app.route('/historie-fotky')
@cached()
def history(year=None):
    all_texts = HistoryText.find_all()

    if year:
        text = HistoryText(year)
        if not text:
            abort(404)
        return render_template('history_detail.html', year=year, text=text,
                               all_texts=all_texts)
    return render_template('history.html', all_texts=all_texts)
