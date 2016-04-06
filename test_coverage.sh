#!/usr/bin/env dash
# coverage will find papers/managment/commands with --source=papers unless
# there's an --omit param, in which case you have specify it separately
coverage run --source=papers,papers/management/commands --omit='papers/migrations/*','*/test_*','*/__init__.py','*/urls.py' --branch manage.py test papers
coverage report -m
coverage erase
# and yet... I don't have to specify utl_files/management/commands. ?!?!
coverage run --source=utl_files --omit='utl_files/migrations/*','*/__init__.py','*/test_*','*/urls.py' --branch manage.py test utl_files
coverage report -m
coverage erase
