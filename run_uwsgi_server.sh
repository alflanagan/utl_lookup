#!/usr/bin/env bash
# see https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/uwsgi/
# and https://uwsgi.readthedocs.org/en/latest/tutorials/Django_and_nginx.html
export LANG=en_US.UTF-8

BASE_DIR=/mnt/extra/Devel
# PYVENV_DIR=/mnt/extra/python-environments/utl_lookup
PIDFILE=/tmp/utl_lookup-master.pid

# . ${PYVENV_DIR}/bin/activate

cd ${BASE_DIR}

echo "Calling /usr/local/bin/uwsgi"

/usr/local/bin/uwsgi --chdir=${BASE_DIR}/utl_lookup \
    --module=utl_lookup.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=utl_lookup.settings \
    --master --pidfile=${PIDFILE} \
    --socket=127.0.0.1:8001 \
    --processes=2 \
    --uid=985 --gid=981 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum \
    --py-programname=/usr/local/bin/python3.5 \
    --pythonpath /usr/local/lib/python3.5/site-packages \
    --pythonpath ${BASE_DIR}/utl_lookup \
    --pythonpath ${BASE_DIR}/utl_indexer \
    --pythonpath ${BASE_DIR}/shared_libraries \
    --daemonize=/var/log/uwsgi/utl_lookup.log
ERR=$?

if [ $ERR -ne 0 ]; then
    echo /usr/local/bin/uwsgi exited with error code ${ERR}.
fi
exit ${ERR}
