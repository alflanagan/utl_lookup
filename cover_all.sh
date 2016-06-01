#!/usr/bin/env bash
# -*- encoding: utf-8; -*-

if [[ -n "${VIRTUAL_ENV}" ]]; then
    cd $(< $VIRTUAL_ENV/.project)
fi

# don't just run coverage run manage.py test
# because we want to see how each test file covers the associated module
coverage run --source=utl_files.models --branch ./manage.py test utl_files.test_models
coverage run --source=utl_files.views --branch --append ./manage.py test utl_files.test_views
coverage run --source=papers.models --branch --append ./manage.py test papers.test_models
coverage run --source=papers.views --branch --append ./manage.py test papers.test_views
coverage report -m
