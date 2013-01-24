# -*- coding: utf-8 -*-


import re
from fabric.api import *
from datetime import datetime


def deploy():
    # parse active branch
    branches = local('git branch --no-color 2> /dev/null', capture=True)
    match = re.search(r'\* ([\w\-_]*)', branches)
    if not match:
        abort('Unable to detect git branch.')
    branch = match.group(1)

    # push to Heroku
    local('git push heroku {0}:master'.format(branch))

    # push to Github
    tag = 'v' + datetime.utcnow().strftime('%Y.%m.%d')
    local('git tag {0}'.format(tag))
    local('git push --tags origin {0}:master'.format(branch))
