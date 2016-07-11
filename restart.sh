#!/usr/local/bin/dash
PIDFILE=/tmp/utl_lookup-master.pid
MAINDIR=/mnt/extra/Devel/utl_lookup

${MAINDIR}/do_collectstatic.sh

if [ -f ${PIDFILE} ]; then
    /usr/local/bin/uwsgi --stop ${PIDFILE}
fi

sleep 1  # need to give other instance time to release socket
rm -f ${PIDFILE}

echo ${MAINDIR}/run_uwsgi_server.sh

${MAINDIR}/run_uwsgi_server.sh

