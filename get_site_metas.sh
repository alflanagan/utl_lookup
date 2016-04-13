#!/usr/bin/env dash

TOPDIR=/mnt/extra/Devel/utl_indexer/data/exported

for SITE in agnet.net  dothaneagle.com  omaha.com  richmond.com
do
    ./manage.py import_site_meta ${SITE} ${TOPDIR}/${SITE}
done

