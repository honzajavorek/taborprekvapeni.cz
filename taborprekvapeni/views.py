import os
from hashlib import sha1
from io import BytesIO
from collections import OrderedDict
from pathlib import Path
from operator import itemgetter

import times
import yaml
from flask import (render_template, abort, request, send_from_directory,
                   send_file)

from . import app, cache
from .models import BasicInfo, TeamMemberText, Photo


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
    next_ = now.year if now.month <= 6 else now.year + 1

    try:
        starts_at = info['senior']['starts_at']
    except KeyError:
        starts_at = None

    return {
        'info': info,
        'now': now,
        'volume_year': starts_at.year if starts_at else next_,
        'volume_no': (starts_at.year if starts_at else next_) - 1997,
        'is_past': now.date() >= starts_at if starts_at else True,
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


def has_content(history_detail):
    return (
        history_detail.get('name')
        and history_detail.get('place')
    )


@app.route('/historie-fotky/<int:year>')
@app.route('/historie-fotky')
@cache.cached_view()
def history(year=None):
    path = Path(__file__).parent / 'models' / 'history'
    history = sorted([
        dict(year=yml_path.stem, **yaml.safe_load(yml_path.read_text()))
        for yml_path in path.glob('**/*.yml')
    ], key=itemgetter('year'), reverse=True)
    history = list(filter(has_content, history))

    if not year:
        # index page with listing
        return render_template('history.html', history=history)

    try:
        yml_path = path / (str(year) + '.yml')
        history_detail = yaml.safe_load(yml_path.read_text())
    except IOError:
        abort(404)

    if not has_content(history_detail):
        abort(404)
    return render_template('history_detail.html', year=year, **history_detail)


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
    response = send_file(BytesIO(photo), mimetype='image/jpeg')
    response.set_etag(sha1(photo).hexdigest())
    response.make_conditional(request)
    return response


@app.route('/favicon.ico')
def favicon():
    static_dir = os.path.join(app.root_path, 'static')
    mimetype = 'image/vnd.microsoft.icon'
    return send_from_directory(static_dir, 'favicon.ico', mimetype=mimetype)
