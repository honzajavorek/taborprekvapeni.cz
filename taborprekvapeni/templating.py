# -*- coding: utf-8 -*-


import re
import os
import random

import lxml
import unidecode
from flask import request
from jinja2 import Markup
from flask.ext.markdown import Markdown

from taborprekvapeni import app


@app.before_request
def init_markdown():
    # To prevent incremental numbering of headerids,
    # instance of Markdown is created and registered
    # before each HTTP request.
    md = Markdown(app, **app.config['MARKDOWN'])
    app.jinja_env.filters['markdown'] = md


months = (u'ledna', u'února', u'března', u'dubna', u'května', u'června',
          u'července', u'srpna', u'září', u'října', u'listopadu', u'prosince')


@app.template_filter()
def file_exists(filename):
    path = os.path.join(app.root_path, filename)
    return os.path.exists(path)


@app.template_filter()
def date(dt):
    return u'{}.\xa0{}'.format(dt.day, months[dt.month - 1])


@app.template_filter()
def date_range(dt_from, dt_to):
    s = u'od\xa0{}.'.format(dt_from.day)
    if dt_from.month != dt_to.month:
        s += u'\xa0{}'.format(months[dt_from.month - 1])
    s += u'\xa0do\xa0{}.\xa0{}'.format(dt_to.day, months[dt_to.month - 1])
    return s


@app.template_filter()
def slugify(string, sep='_'):
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', sep, string)


@app.template_filter()
def email(address):
    username, server = address.split('@')
    email_markup_fmt = (
        '<a href="mailto:{username}&#64;{server}">'
        '{username}&#64;<!---->{server}</a>'
    )
    markup = (email_markup_fmt).format(username=username, server=server)
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


@app.template_filter()
def members_showcase(members, n=5):
    return members[:5] + random.sample(members[5:], n)
