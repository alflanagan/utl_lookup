#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command to list the Townnews packages stored in the database.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""

from django.core.management.base import BaseCommand
from utl_files.models import Package


class Command(BaseCommand):
    """Command to list the Townnews packages stored in the database."""
    help = 'Lists all Townnews packages currently known. Warning: list may be long.'

    # def add_arguments(self, parser):
    #     parser.add_argument('pkg_name', help='OfficeTownnews package')

    def handle(self, *args, **options):
        for pkg in Package.objects.all():
            isinstance(pkg, Package)
            print("{}: {}".format(pkg.name, pkg.version))
