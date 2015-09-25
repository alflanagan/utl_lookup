from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from utl_files.models import Package, PackageError


class Command(BaseCommand):
    help = 'Imports the given directory as a Townnews package.'

    def add_arguments(self, parser):
        parser.add_argument('directory', help='parent directory of the Townnews package')

    def handle(self, *args, **options):
        path = Path(options['directory'])
        if not path.is_dir():
            raise CommandError("Not a directory: {}".format(path))
        try:
            Package.load_from(path)
        except PackageError as perr:
            raise CommandError(str(perr))
        self.stdout.write("Load from {} complete.".format(path))
