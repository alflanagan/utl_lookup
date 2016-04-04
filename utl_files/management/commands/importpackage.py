# -*- coding:utf-8 -*-
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from utl_files.models import Package, PackageError, TownnewsSite
from utl_lib.tn_package import TNPackage

# pylint: disable=no-member


class Command(BaseCommand):
    help = 'Imports the given directory as a Townnews package.'

    def add_arguments(self, parser):
        parser.add_argument('directory', help='parent directory of the Townnews package')

    def handle(self, *args, **options):
        path = Path(options['directory'])
        if not path.is_dir():
            raise CommandError("Not a directory: {}".format(path))
        try:
            path = path.resolve()
            pkg_type = None
            # get site, dir from path
            for key in TNPackage.PKG_DIRS:
                if TNPackage.PKG_DIRS[key] in [path.parent.name, path.parent.parent.name]:
                    pkg_type = key
            if pkg_type is None:
                raise CommandError("Can't get package type from {}.".format(path))
            # print("pkg_type is " + pkg_type)

            # all this fiddly logic should probably go in its own class
            site_name = path.parent.parent.name
            if site_name == 'skins':
                site_name = path.parent.parent.parent.name
            if site_name == "certified":
                site = None
            else:
                site = TownnewsSite.objects.get(URL="http://{}".format(site_name))

            # print("site is " + site_name)
            Package.load_from(path, site, pkg_type)
        except PackageError as perr:
            raise CommandError(str(perr))
        self.stdout.write("Load from {} complete.".format(path))
