# -*- coding:utf-8 -*-
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from utl_files.models import Package, PackageError


class Command(BaseCommand):
    help = 'Lists all Townnews packages currently known. Warning: list may be long.'

    def add_arguments(self, parser):
        parser.add_argument('package-name', help='Townnews package name', metavar='PKG-NAME')
        parser.add_argument('package-ver', help='package version number', metavar='PKG-VERSION')

    def handle(self, *args, **options):
        try:
            pkg = Package.objects.get(name=options['package-name'], version=options['package-ver'])
            pkg.delete()
        except Package.DoesNotExist:
            raise CommandError("Can't remove package '{}' ({}) as it is not present "
                               "(try manage.py listpackages.)".format(options['package-name'],
                                                                   options['package-ver']))
