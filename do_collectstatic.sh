#!/usr/local/bin/dash
# run collectstatic with all the "extras" needed to run as random user
PYTHON=/usr/local/bin/python3.5 
BASEDIR=/mnt/extra/Devel
SITEDIR=${BASEDIR}/utl_lookup

PYTHONPATH=${SITEDIR}:${BASEDIR}/utl_indexer:${BASEDIR}/shared_libraries ${PYTHON} ${SITEDIR}/manage.py collectstatic --noinput
