#!/usr/bin/env dash
# run tests with warnings enabled, except specific ones from library modules
python -Wall -Wignore:::django.dispatch.dispatcher:99 -Wignore:::django.template.base:1189 -Wignore:::django.utils.six:80 manage.py test $*

