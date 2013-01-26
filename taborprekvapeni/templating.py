# -*- coding: utf-8 -*-


from jinja2 import Markup
from flask.ext.markdown import Markdown
from flask import url_for as original_url_for

from taborprekvapeni import app, __version__ as version


def url_for(endpoint, **values):
    url = original_url_for(endpoint, **values)
    if endpoint == 'static':
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


@app.template_filter()
def email(address):
    username, server = address.split('@')
    markup = ('<a href="mailto:{username}&#64;{server}">'
              '{username}&#64;<!---->{server}</a>').format(username=username,
                                                           server=server)
    return Markup(markup)
