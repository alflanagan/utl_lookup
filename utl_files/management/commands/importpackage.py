#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command to import a set of package files into the database.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

from utl_files.models import Package, PackageError, TownnewsSite
from utl_lib.tn_package import TNPackage

# pylint: disable=no-member


class Command(BaseCommand):
    """Command to import a package from the filesystem."""
    help = 'Imports the given directory as a Townnews package.'

    # TODO: --replace flag replaces package if it's already in database.
    def add_arguments(self, parser):
        parser.add_argument('directory', help='parent directory of the Townnews package')

    def handle(self, *args, **options):
        pkg_path = Path(options['directory'])
        error_flag = False  # hack
        if not pkg_path.is_dir():
            raise CommandError("Not a directory: {}".format(pkg_path))
        try:
            pkg_path = pkg_path.resolve()  # pylint:disable=R0204
            pkg_type = None
            # get site, dir from path
            for key in TNPackage.PKG_DIRS:
                if TNPackage.PKG_DIRS[key] in [pkg_path.parent.name, pkg_path.parent.parent.name]:
                    pkg_type = key
            if pkg_type is None:
                raise CommandError("Can't get package type from {}.".format(pkg_path))
            # print("pkg_type is " + pkg_type)

            # all this fiddly logic should probably go in its own class
            site_name = pkg_path.parent.parent.name
            if site_name == 'skins':
                site_name = pkg_path.parent.parent.parent.name
            if site_name == "certified":
                site = None
            else:
                try:
                    site = TownnewsSite.objects.get(URL="http://{}".format(site_name))
                except TownnewsSite.DoesNotExist:
                    sys.stderr.write("I can't find a site record for http://{}. Create "
                                     "one and try again.".format(site_name))
                    sys.exit(2)

            # print("site is " + site_name)
            try:
                Package.load_from(pkg_path, site, pkg_type)
            except ValidationError as verr:
                if "__all__" in verr.message_dict and verr.message_dict['__all__']:
                    msg = verr.message_dict['__all__'][0]
                    if msg.startswith('Unique constraint violation:'):
                        sys.stderr.write(msg.replace('Unique constraint violation: ',
                                                     'Not loaded:') + '\n')
                        error_flag = True
                    else:
                        raise
                else:
                    raise

        except PackageError as perr:
            raise CommandError(str(perr))
        if not error_flag:
            self.stdout.write("Load from {} complete.".format(pkg_path))
