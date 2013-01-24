# -*- coding: utf-8 -*-


import re
import os
from fabric.api import *


base_path = os.path.dirname(__file__)
version_file = 'setup.py'


if os.getcwd() != base_path:
    abort('Not in project root. Please, cd to {0}.'.format(base_path))


__all__ = ('deploy', 'ps', 'logs')


def capture(cmd):
    with settings(hide('warnings', 'running', 'stdout', 'stderr'),
                  warn_only=True):
        return local(cmd, capture=True)


def bump_version():
    """Automatically bump version."""
    version_re = re.compile(r"version='([^']+)'")

    with open(version_file) as f:
        code = f.read()
    try:
        match = version_re.search(code)
        version = match.group(1)
    except AttributeError:
        abort('Unable to detect current version.')

    major, minor, micro = map(int, version.split('.'))
    micro += 1
    version = '.'.join(map(str, [major, minor, micro]))

    puts('Bumping version to {0}.'.format(version))
    code = version_re.sub("version='{0}'".format(version), code)

    with open(version_file, 'w') as f:
        f.write(code)
    return version


def check_repo():
    """Check if repository is ready for deployment."""
    ahead = capture('git status | grep -e "branch is ahead"')
    if not ahead:
        abort('Nothing to deploy.')
    staged = capture('git status -s | grep -e "^M"')
    if staged:
        abort('Staged modified files present in repository.')
    modified = capture('git status -s | grep "M {0}"'.format(version_file))
    if modified:
        abort('File with version {0} is modified, '
              'but not commited.'.format(version_file))


def deploy():
    """Deploy site to Heroku."""
    # parse active branch
    branches = capture('git branch --no-color 2> /dev/null')
    match = re.search(r'\* ([\w\-_]*)', branches)
    if not match:
        abort('Unable to detect git branch.')
    branch = match.group(1)

    # check repository status
    check_repo()

    # push to Heroku
    local('git push heroku {0}:master'.format(branch))
    local('heroku ps:scale web=1')

    # push to Github
    tag = 'v' + bump_version()
    local('git add ' + version_file)
    local('git commit --amend --no-edit')
    local('git tag {0}'.format(tag))
    local('git push --tags origin {0}:master'.format(branch))


def ps():
    """Show remote process list."""
    local('heroku ps')


def logs():
    """Show remote logs."""
    local('heroku logs')
