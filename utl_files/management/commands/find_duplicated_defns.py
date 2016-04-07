# -*- coding:utf-8 -*-
from collections import defaultdict
from django.core.management.base import BaseCommand, CommandError
from utl_files.models import UTLFile, MacroDefinition


def create_defdict(some_type):
    """A function allowing us to create a defaultdict whose type is defaultdict(int)"""
    return lambda: defaultdict(some_type)


# pylint:disable=no-member
def print_dup_macro_defns():
    definitions = defaultdict(create_defdict(int))

    for utl_file in UTLFile.objects.all():
        for macro_def in MacroDefinition.objects.filter(source=utl_file):
            definitions[utl_file][macro_def.name] += 1

    # TODO: needs better formatting, line up columns and headers
    print("UTL Files defining a macro more than once:")
    print("Package           Version    File                          Macro Name   Times Defined")
    for utl_file in definitions:
        for macro_name in definitions[utl_file]:
            if definitions[utl_file][macro_name] > 1:
                print(utl_file.pkg.name, utl_file.pkg.version, utl_file.file_path, macro_name,
                      definitions[utl_file][macro_name])


class Command(BaseCommand):
    help = 'Searches for UTL files that define a macro of the same name more than once.'

    def handle(self, *args, **options):
        print_dup_macro_defns()
