import os
from django.core.management.base import BaseCommand, CommandError
from utl_files.models import Package


class Command(BaseCommand):
    help = 'Imports the given directory as a Townnews package.'

    def add_arguments(self, parser):
        parser.add_argument('directory', help='parent directory of the Townnews package')

    def handle(self, *args, **options):
        if not os.path.isdir(options['directory']):
            raise CommandError("Not a directory: {}".format(options['directory']))
        Package.load_from(options['directory'])
        self.stdout.write("Load from {} complete.".format(options['directory']))
