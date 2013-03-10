# -*- coding: utf-8 -*-


import os
import times
from flask import render_template, abort, request, send_from_directory

from taborprekvapeni import app
from taborprekvapeni.cache import cached
from taborprekvapeni.image import Image, generated_image
from taborprekvapeni.templating import url_for, minified
from taborprekvapeni.models import (BasicInfo, HistoryText, PhotoAlbums,
                                    TeamMemberText)


@app.context_processor
def redefine():
    return {'url_for': url_for}


@app.context_processor
def inject_config():
    return {'ga_code': app.config['GA_CODE'],
            'debug': app.debug}


@app.context_processor
def inject_info():
    info = BasicInfo()

    now = times.to_local(times.now(), 'Europe/Prague')
    starts_at = info['senior']['starts_at']
    ends_at = info['senior']['ends_at']

    return {
        'info': info,
        'volume_year': starts_at.year,
        'volume_no': starts_at.year - 1997,
        'is_past': now.date() > ends_at,
        'countdown': (starts_at - now.date()).days,
    }


@app.route('/')
@cached
@minified
def index():
    members = list(TeamMemberText.find_all())
    return render_template('index.html', members=members)


@app.route('/filozofie-napln')
@cached
@minified
def program():
    return render_template('program.html')


@app.route('/informace')
@cached
@minified
def info():
    return render_template('info.html')


@app.route('/kontakty')
@cached
@minified
def contact():
    return render_template('contact.html')


@app.route('/tym-vedoucich/<slug_url>')
@app.route('/tym-vedoucich')
@cached
@minified
def team(slug_url=None):
    all_texts = TeamMemberText.find_all()

    if not slug_url:
        # index page with listing
        return render_template('team.html', all_texts=all_texts)

    text = TeamMemberText.from_slug_url(slug_url) or abort(404)
    return render_template('team_detail.html', text=text,
                           all_texts=all_texts)


@app.route('/historie-fotky/<int:year>')
@app.route('/historie-fotky')
@cached
@minified
def history(year=None):
    all_texts = HistoryText.find_all()

    if not year:
        # index page with listing
        return render_template('history.html', all_texts=all_texts)

    all_albums = PhotoAlbums()
    text = HistoryText(year)
    albums = all_albums.get(year, [])

    has_content = any([
        # has non-empty text
        text,
        # has essential attributes and albums
        text.title and text.place and all_albums.get(year),
    ])

    if not has_content:
        abort(404)
    return render_template('history_detail.html', year=year, text=text,
                           all_texts=all_texts, albums=albums)


@app.route('/image')
@generated_image
def image_proxy():
    url = request.args.get('url') or abort(404)

    w, h = request.args.get('resize', 'x').split('x')
    crop = request.args.get('crop')

    img = Image.from_url(url)
    img.rotate()

    if crop:
        img.crop(int(crop))
    if w and h:
        img.resize_crop(int(w), int(h))
    img.sharpen()

    return img.to_stream()


@app.route('/favicon.ico')
def favicon():
    static_dir = os.path.join(app.root_path, 'static')
    return send_from_directory(static_dir, 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')
