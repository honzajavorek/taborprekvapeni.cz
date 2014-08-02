# -*- coding: utf-8 -*-


import os
from hashlib import sha1
from StringIO import StringIO
from collections import OrderedDict

import times
from flask import (render_template, abort, request, send_from_directory,
                   send_file)

from . import app, cache
from .models import BasicInfo, TeamMemberText, HistoryText, PhotoAlbums, Photo


@app.context_processor
def inject_config():
    return {
        'ga_code': app.config['GA_CODE'],
        'debug': app.debug,
    }


@app.context_processor
def inject_info():
    info = cache.cached_call('basic-info', BasicInfo)

    now = times.to_local(times.now(), 'Europe/Prague')
    starts_at = info['senior']['starts_at']

    return {
        'info': info,
        'now': now,
        'volume_year': starts_at.year,
        'volume_no': starts_at.year - 1997,
        'is_past': now.date() >= starts_at,
        'countdown': (starts_at - now.date()).days,
    }


@app.route('/')
@cache.cached_view()
def index():
    members = list(TeamMemberText.all())
    return render_template('index.html', members=members)


@app.route('/filozofie-napln')
@cache.cached_view()
def program():
    return render_template('program.html')


@app.route('/informace')
@cache.cached_view()
def info():
    return render_template('info.html')


@app.route('/kontakty')
@cache.cached_view()
def contact():
    return render_template('contact.html')


@app.route('/tym-vedoucich/<slug>')
@app.route('/tym-vedoucich')
@cache.cached_view()
def team(slug=None):
    all_texts = TeamMemberText.all()

    if not slug:
        # index page with listing
        return render_template('team.html', all_texts=all_texts)

    text = TeamMemberText.from_slug(slug) or abort(404)
    return render_template('team_detail.html', text=text,
                           all_texts=all_texts)


@app.route('/historie-fotky/<int:year>')
@app.route('/historie-fotky')
@cache.cached_view()
def history(year=None):
    all_albums = OrderedDict(cache.cached_call('photo-albums', PhotoAlbums))
    all_texts = HistoryText.all()

    if not year:
        # index page with listing
        return render_template('history.html', all_texts=all_texts)

    text = HistoryText(year)
    albums = all_albums.get(year, [])

    has_content = any([
        text,  # has non-empty text
        text.title and text.place and albums,  # has essential attributes
    ])

    if not has_content:
        abort(404)
    return render_template('history_detail.html', year=year, text=text,
                           all_texts=all_texts, albums=albums)


@app.route('/image')
@cache.cached_view(key='view/{request.path}{request.args[url]}')
def image_proxy():
    # params
    url = request.args.get('url') or abort(404)
    resize = request.args.get('resize')
    if resize:
        width, height = resize.split('x')
        if width and height:
            resize = (int(width), int(height))
    crop = request.args.get('crop')

    # get photo's bytes
    photo = Photo(url, crop=crop, resize=resize)

    # build response
    response = send_file(StringIO(photo), mimetype='image/jpeg')
    response.set_etag(sha1(photo).hexdigest())
    response.make_conditional(request)
    return response


@app.route('/favicon.ico')
def favicon():
    static_dir = os.path.join(app.root_path, 'static')
    mimetype = 'image/vnd.microsoft.icon'
    return send_from_directory(static_dir, 'favicon.ico', mimetype=mimetype)
