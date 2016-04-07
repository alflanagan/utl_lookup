#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defines a command to remove all Townnews packages from the database.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from django.core.management.base import BaseCommand
from utl_files.models import Package


# TODO: Either remove this post-development or make it much harder to do
class Command(BaseCommand):
    """Drop all Townnews packages from database."""
    help = 'Drops all Townnews packages currently known.'

    def handle(self, *args, **options):
        Package.objects.all().delete()
