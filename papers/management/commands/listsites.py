# -*- coding:utf-8 -*-
"""Managment command to list web sites."""
import sys
from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from papers.models import TownnewsSite, NewsPaper


class Command(BaseCommand):
    """A command that lists web sites from the database."""
    help = 'Prints a list of the web sites known to this app.'

    # pylint: disable=redefined-variable-type
    def handle(self, *args, **options):
        url_width = name_width = paper_width = 0
        for tnsite in TownnewsSite.objects.all():
            url_width = max(url_width, len(tnsite.URL))
            name_width = max(name_width, len(tnsite.name))
            paper_width = max(paper_width, len(tnsite.paper.name))
        url_width += 5
        name_width += 5
        paper_width += 5
        print("{:{}} {:{}} {:{}}".format("URL", url_width,
                                         "Site", name_width,
                                         "Paper", paper_width))
        print("-" * (2 + url_width + name_width + paper_width))

        for tnsite in TownnewsSite.objects.all():
            print("{:{}} {:{}} {:{}}".format(tnsite.URL, url_width,
                                             tnsite.name, name_width,
                                             tnsite.paper.name, paper_width))
