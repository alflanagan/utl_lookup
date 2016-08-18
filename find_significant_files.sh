#!/usr/bin/env dash
# list all files that aren't derived, copied, external, git internals, etc.
EXCLUDE_FLAG=""
for EXCLUDE in external data test_data .git __pycache__ node_modules doc TAGS jsdocs
do
    EXCLUDE_FLAG="${EXCLUDE_FLAG} -name ${EXCLUDE} -prune -o"
done

find . ${EXCLUDE_FLAG} -path './static/*' -o -type f -print
