#!/usr/bin/env dash

if [ $# -lt 1 -o "$1" = "-h" -o "$1" = "--help" ]; then
    echo "Usage: $(basename $0) FILE [FILE...]"
    echo "    Compiles each specified FILE with lessc, creating .css and .css.map files"
    echo "    in the same directory."
    exit 0
fi

MY_LOG=/mnt/extra/Devel/utl_lookup/buildcss.log

for LESS_FILE in "$@"
do
    # don't process hidden files, they're editor temporaray copies
    if [ "${LESS_FILE#.}" = "${LESS_FILE}" ]; then
        CSS_FILE=${LESS_FILE%.less}.css
        
        echo "$(date '+%y%m%d %H:%M:%S') ${LESS_FILE}" >> ${MY_LOG}
        
        # watchman will call this if file deleted, so make sure it still exists.
        # (see 'watchless' script)
        if [ -f ${LESS_FILE} ]; then
            exec lessc  --source-map --strict-math=on --strict-units=on ${LESS_FILE} ${CSS_FILE}
        fi
    fi
done
