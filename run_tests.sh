#!/usr/bin/env dash
# run tests with warnings enabled, except specific ones from library modules

if [ "$1" != "--cover" ]; then
    python -Wall -Wignore:::django.dispatch.dispatcher:99 -Wignore:::django.template.base:1189 -Wignore:::django.utils.six:80 manage.py test $*
else
    coverage run --source='.' --omit='*/migrations/*','utl_lookup/dev-settings.py','utl_files/test_models.py','*/admin.py','utl_lookup/wsgi.py' manage.py test
    coverage report --omit='*/__init__.py'
    coverage report -m utl_files/models.py
fi
