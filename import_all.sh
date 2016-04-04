#!/usr/bin/env dash
# import all the package directories created by the
# utl_index/unpack_zip_files.py process

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
                        # echo importing ${PKG}
                        ./manage.py importpackage ${PKG}
                        ERR=$?
                        if [ ${ERR} -ne 0 ]; then
                            echo "${PKG} import failed with code ${ERR}." >&2
                            exit ${ERR}
                        fi
                    done
                done
            else
                for PKG in ${PKG_TYPE}/*
                do
                    # echo Importing ${PKG}
                    ./manage.py importpackage ${PKG}
                    ERR=$?
                    if [ ${ERR} -ne 0 ]; then
                        echo "${PKG} import failed with code ${ERR}." >&2
                        exit ${ERR}
                    fi
                done
            fi
        fi
    done
done
