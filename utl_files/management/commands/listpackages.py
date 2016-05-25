#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command to list the Townnews packages stored in the database.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""

from django.core.management.base import BaseCommand, CommandParser
from utl_files.models import Package, PackageProp


class Command(BaseCommand):
    """Command to list the Townnews packages stored in the database."""
    help = 'Lists all Townnews packages currently known. Warning: list may be long.'

    PKG_TYPE_LOOKUP = {"global": Package.GLOBAL_SKIN,
                       "skin": Package.SKIN,
                       "block": Package.BLOCK,
                       "component": Package.COMPONENT}

    def add_arguments(self, parser):
        super().add_arguments(parser)  # not strictly necessary, but...
        isinstance(parser, CommandParser)
        # type_choices = list(self.PKG_TYPE_LOOKUP.values()).append("all")
        # aggravatingly, add_argument() doesn't show dynamic list in help
        # output
        parser.add_argument('pkg_type', help='Package type (default = all)',
                            default='all', nargs='?',
                            choices=["global", "skin", "block", "component", "all"])

    def handle(self, *args, **options):
        if 'pkg_type' not in options or options['pkg_type'] == "all":
            pkgs = Package.objects.all()
        else:
            pkg_type = self.PKG_TYPE_LOOKUP[options['pkg_type']]
            pkgs = Package.objects.filter(pkg_type=pkg_type)

        for pkg in pkgs.order_by("site", "name"):
            isinstance(pkg, Package)
            try:
                title = pkg.packageprop_set.get(key="title").value
            except PackageProp.DoesNotExist:  # pylint: disable=E1101
                title = pkg.name
            if pkg.site is not None:
                if title == pkg.name:
                    print("{} - {} {}".format(pkg.site.domain,
                                                     pkg.name,
                                                     pkg.version))
                else:
                    print("{} - '{}' ({}) {}".format(pkg.site.domain,
                                                     title, pkg.name,
                                                     pkg.version))
            else:
                if title == pkg.name:
                    print("certified - {} {}".format(pkg.name, pkg.version))
                else:
                    print("certified - '{}' ({}) {}".format(title, pkg.name,
                                                            pkg.version))
