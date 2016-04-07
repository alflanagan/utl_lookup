# -*- coding:utf-8 -*-
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from utl_files.models import Package, PackageError


class Command(BaseCommand):
    help = 'Lists all Townnews packages currently known. Warning: list may be long.'

    # def add_arguments(self, parser):
    #     parser.add_argument('pkg_name', help='OfficeTownnews package')

    def handle(self, *args, **options):
        for pkg in Package.objects.all():
            isinstance(pkg, Package)
            print("{}: {}".format(pkg.name, pkg.version))
