#!/usr/bin/env dash
cd /mnt/extra/Devel/utl_lookup
coverage run --source=papers,utl_files --omit='*/migrations/*','*/test_*','*/__init__.py','*/urls.py' --branch manage.py test papers utl_files
coverage report -m
coverage erase
