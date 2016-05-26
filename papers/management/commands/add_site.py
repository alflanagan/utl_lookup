# -*- coding:utf-8 -*-
"""Managment command to manually add a web site."""
import sys
from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from papers.models import TownnewsSite, NewsPaper


class Command(BaseCommand):
    """A command that adds a new site."""
    help = 'Adds a new site to the TownnewsSite table.'

    def add_arguments(self, parser):
        isinstance(parser, ArgumentParser)
        parser.add_argument('domain', help='The domain of the site (ex.: richmond.com)')
        parser.add_argument('name', help='The common name of the site (may be same as domain)')
        parser.add_argument('paper', help='The name of the newspaper that owns the site.')

    # pylint: disable=redefined-variable-type
    def handle(self, *args, **options):
        the_paper = 'Error!'
        try:
            the_paper = NewsPaper.objects.get(name=options['paper'])
        except NewsPaper.DoesNotExist:
            print("I don't see a newspaper named '{}'.".format(options['paper']))
            reply = 'A'
            while not reply.startswith(('C', 'c')):
                print("C)reate newspaper '{}', L)ist existing papers, Q)uit:".format(options[
                    'paper']))
                reply = sys.stdin.readline()
                if reply.startswith(('Q', 'q')):
                    return
                if reply.startswith(('L', 'l')):
                    print('    Papers')
                    print('    -------------------------')
                    for paper in NewsPaper.objects.all():
                        print('    ' + paper.name)
                elif reply.startswith(('C', 'c')):
                    print("creating")
                    the_paper = NewsPaper(name=options['paper'])
                    the_paper.full_clean()
                    the_paper.save()
                    print("Created NewsPaper '{}'".format(options['paper']))

        new_url = options['domain']
        if not new_url.startswith('http'):
            new_url = "http://" + new_url
        new_site = TownnewsSite(URL=new_url, name=options['name'], paper=the_paper)
        new_site.full_clean()
        new_site.save()
        print("Successfully created new site {}.".format(new_site))
