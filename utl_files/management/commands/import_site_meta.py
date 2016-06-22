#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command to import the site-related metadata into the database.

Currently this is just a list of the certified pacakges used by the site.

| © 2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from pathlib import Path
import sys

from django.core.management.base import BaseCommand, CommandError

from utl_files.models import Package, TownnewsSite, CertifiedUsedBy
from utl_lib.tn_site import TNSiteMeta

# pylint: disable=no-member


class Command(BaseCommand):
    """Command to import a sites metadata file."""
    help = 'Imports the given directory as a Townnews package.'

    def add_arguments(self, parser):
        parser.add_argument('site_name', help='The domain of the site. (ex. "richmond.com")')
        parser.add_argument('directory', help='Root site export directory.')

    def handle(self, *args, **options):
        site_name = options["site_name"]
        try:
            the_site = TownnewsSite.objects.get(URL='http://' + site_name)
        except TownnewsSite.DoesNotExist:
            raise CommandError("Site '{}' is not in the database."
                               "".format('http://' + site_name))
        site_path = Path(options['directory'])
        if not site_path.is_dir():
            raise CommandError("Not a directory: {}".format(site_path))
        site_path = site_path.resolve()  # pylint:disable=R0204
        site_meta = TNSiteMeta(site_name, site_path)
        for pkg_name in site_meta.data:
            pkg_data = site_meta.data[pkg_name]
            if pkg_data["certified"] == "Y":
                # print("Checking for package {}".format(pkg_name))
                try:
                    the_pkg = Package.objects.get(name=pkg_name,
                                                  version=pkg_data["version"],
                                                  is_certified=True)
                except Package.DoesNotExist:
                    sys.stderr.write("Warning: Package {}/{} not found.\n"
                                     "".format(pkg_name, pkg_data["version"]))
                else:
                    _, was_created = CertifiedUsedBy.objects.get_or_create(site=the_site,
                                                                           package=the_pkg)
                    if was_created:
                        print("Created used_by for package {}".format(the_pkg.name))
