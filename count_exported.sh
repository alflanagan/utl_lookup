#!/usr/bin/env bash
# import all the package directories created by the
# utl_index/unpack_zip_files.py process

COUNT=0

for SITE in  ../utl_indexer/data/exported/*
do
    for PKG_TYPE in ${SITE}/*
    do
        if [ -d ${PKG_TYPE} ]; then  # skip site_meta.json, etc.
            if [ $(basename ${PKG_TYPE}) = skins ]; then
                for APP in ${PKG_TYPE}/*
                do
                    for PKG in ${APP}/*
                    do
                        (( COUNT = COUNT + 1 ))
                    done
                done
            else
                for PKG in ${PKG_TYPE}/*
                do
                    (( COUNT = COUNT + 1 ))
                done
            fi
        fi
    done
done

echo "Found ${COUNT} packages ready for import."
