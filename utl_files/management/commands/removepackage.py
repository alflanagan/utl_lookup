# -*- coding:utf-8 -*-
"""Convenient manage.py command to remove a package from the database."""
from django.core.management.base import BaseCommand, CommandError
from utl_files.models import Package, TownnewsSite

# pylint:disable=no-member

class Command(BaseCommand):
    """Command 'manage.py removepackage'."""
    help = 'Removes a stored Townnews package.'

    def add_arguments(self, parser):
        parser.add_argument('package-site', help='Site URL', metavar='PKG-SITE')
        parser.add_argument('package-name', help='Townnews package name', metavar='PKG-NAME')
        parser.add_argument('package-ver', help='package version number', metavar='PKG-VERSION')

    def handle(self, *args, **options):
        try:
            siteurl = options['package-site']
            siteurl = siteurl if siteurl.startswith('http:') else 'http://' + siteurl
            try:
                site = TownnewsSite.objects.get(URL=siteurl)
            except TownnewsSite.DoesNotExist:
                raise CommandError("Can't find site {}".format(siteurl))
            pkg = Package.objects.get(name=options['package-name'],
                                      version=options['package-ver'],
                                      site=site)
            pkg.delete()
        except Package.DoesNotExist:
            raise CommandError("Can't remove package '{}:{}' ({}) as it is not present "
                               "(try manage.py listpackages.)".format(options['package-site'],
                                                                      options['package-name'],
                                                                      options['package-ver']))
