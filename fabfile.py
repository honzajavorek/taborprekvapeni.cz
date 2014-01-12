# -*- coding: utf-8 -*-


import re
import os
from fabric.api import *  # NOQA


project_dir = os.path.dirname(__file__)


__all__ = ('deploy', 'ps', 'logs')


### Helpers


def capture(cmd):
    with settings(hide('warnings', 'running', 'stdout', 'stderr'),
                  warn_only=True):
        return local(cmd, capture=True)


def read_branch():
    branches = capture('git branch --no-color 2> /dev/null')
    try:
        return re.search(r'\* ([\w\-_]*)', branches).group(1)
    except AttributeError:
        abort('Unable to detect git branch.')


### Tasks

def deploy():
    """Push site to GitHub and deploy it to Heroku."""
    branch = read_branch()

    # push to GitHub
    local('git push origin {0}:{0}'.format(branch))

    # push to Heroku
    local('git push heroku {0}:master'.format(branch))
    if 'web.1: up' not in capture('heroku ps'):
        local('heroku ps:scale web=1')


def ps():
    """Show remote process list."""
    local('heroku ps')


def logs():
    """Show remote logs."""
    local('heroku logs')
