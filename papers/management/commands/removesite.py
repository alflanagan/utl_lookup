# -*- coding:utf-8 -*-
"""Managment command to manually remove a web site."""
import sys
from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from papers.models import TownnewsSite, NewsPaper


class Command(BaseCommand):
    """A command that removes a web site."""
    help = 'Remove a site from the app.'

    def add_arguments(self, parser):
        isinstance(parser, ArgumentParser)
        parser.add_argument('domain', help='The domain of the site (ex.: richmond.com)')

    # pylint: disable=redefined-variable-type
    def handle(self, *args, **options):
        the_site = TownnewsSite.objects.get(URL='http://{}'.format(options["domain"]))
        the_site.delete()
