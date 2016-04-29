#!/usr/bin/env dash
find . -name external -prune -o -name data -prune -o -name test_data -prune -o -name .git -prune -o \
     -name __pycache__ -prune -o -path './static/*' -prune -o -type f -print
