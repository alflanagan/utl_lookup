#!/usr/bin/env bash

for MODEL in TownnewsSite NewsPaper TownnewsSiteMetaData
do
    DEST_NAME=$(echo ${MODEL} | tr '[:upper:]' '[:lower:]')
    ./manage.py dumpdata --indent 2 papers.${MODEL} -o ${DEST_NAME}.json
done

for MODEL in Application MacroDefinition MacroRef Package PackageDep PackageProp UTLFile
do
    DEST_NAME=$(echo ${MODEL} | tr '[:upper:]' '[:lower:]')
    ./manage.py dumpdata --indent 2 utl_files.${MODEL} -o ${DEST_NAME}.json
done
