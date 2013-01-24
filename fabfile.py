# -*- coding: utf-8 -*-


import re
from fabric.api import *
from datetime import datetime


def deploy():
    """Deploy site to Heroku."""
    # parse active branch
    branches = local('git branch --no-color 2> /dev/null', capture=True)
    match = re.search(r'\* ([\w\-_]*)', branches)
    if not match:
        abort('Unable to detect git branch.')
    branch = match.group(1)

    # push to Heroku
    local('git push heroku {0}:master'.format(branch))
    local('heroku ps:scale web=1')

    # push to Github
    tag = 'v' + datetime.utcnow().strftime('%Y.%m.%d')
    local('git tag {0}'.format(tag))
    local('git push --tags origin {0}:master'.format(branch))


def ps():
    """Show remote process list."""
    local('heroku ps')


def open():
    """Open site in browser."""
    local('heroku open')


def logs():
    """Show remote logs."""
    local('heroku logs')
