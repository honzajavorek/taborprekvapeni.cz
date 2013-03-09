# -*- coding: utf-8 -*-


import re
import os
import lxml
import unidecode
from jinja2 import Markup
from functools import wraps
from flask.ext.gzip import Gzip
from flask.ext.markdown import Markdown
from flask import url_for as original_url_for, request

from taborprekvapeni import app, __version__ as version


Gzip(app)


def url_for(endpoint, **values):
    url = original_url_for(endpoint, **values)
    if endpoint in ['static', 'favicon']:
        sep = '&' if ('?' in url) else '?'
        url += '{0}v{1}'.format(sep, version)
    return url


@app.before_request
def before_request():
    md = Markdown(app, **app.config['MARKDOWN'])

    # To prevent incremental numbering of headerids,
    # instance of Markdown is created and registered
    # before each HTTP request.
    app.jinja_env.filters['markdown'] = md


def minified(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        result = f(*args, **kwargs)
        if not app.debug:
            soup = lxml.html.fromstring(result)
            for text in soup.xpath('//text()'):
                if re.match(r'\s+$', text):  # is whitespace
                    if text.is_tail:
                        text.getparent().tail = ' '
                    else:
                        text.getparent().text = ' '
            return lxml.html.tostring(soup, encoding='utf-8')
        else:
            return result
    return decorated_function


@app.template_filter()
def file_exists(filename):
    path = os.path.join(app.root_path, filename)
    return os.path.exists(path)


@app.template_filter()
def date(dt):
    d = dt.strftime('%d. %m.')
    return re.sub(r'0+(\d+)', r'\1', d)


@app.template_filter()
def slugify(string, sep='_'):
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', sep, string)


@app.template_filter()
def email(address):
    username, server = address.split('@')
    markup = ('<a href="mailto:{username}&#64;{server}">'
              '{username}&#64;<!---->{server}</a>').format(username=username,
                                                           server=server)
    return Markup(markup)


@app.template_filter()
def extract_title(html):
    try:
        h1 = lxml.html.fromstring(html).xpath('//h1[1]')[0]
        h1 = re.sub(r'\s+', ' ', h1.text_content()).strip()
        return h1
    except:
        return ''


@app.template_filter()
def extract_image(html):
    try:
        img = lxml.html.fromstring(html).xpath('//img[1]')[0]
        return request.url_root.rstrip('/') + img.get('src')
    except:
        return ''


@app.template_filter()
def split(string, sep):
    return string.split(sep)


@app.template_filter()
def capitalize_first(string):
    return string[0].upper() + string[1:]
