#!/usr/bin/env bash
# -*- encoding: utf-8; -*-

if [[ -n "${VIRTUAL_ENV}" && -f "${VIRTUAL_ENV}/.project" ]]; then
    cd $(< $VIRTUAL_ENV/.project)
fi

do_cover() {
    # don't just run coverage run manage.py test
    # because we want to see how each test file covers the associated module
    coverage run --source="$1.$2" --branch --append ./manage.py test "$1.test_$2"
}

do_cover utl_files models
do_cover utl_files views
do_cover utl_files code_markup
do_cover papers models
do_cover papers views

coverage report -m
