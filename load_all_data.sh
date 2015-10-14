#!/usr/bin/env dash
for DIR in data/tncertified/*
do
     ./manage.py importpackage ${DIR}
done
