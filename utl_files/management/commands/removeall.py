# -*- coding:utf-8 -*-
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from utl_files.models import Package, PackageError


# TODO: Either remove this post-development or make it much harder to do
class Command(BaseCommand):
    help = 'Drops all Townnews packages currently known.'


    def handle(self, *args, **options):
        for pkg in Package.objects.all():
            pkg.delete()
