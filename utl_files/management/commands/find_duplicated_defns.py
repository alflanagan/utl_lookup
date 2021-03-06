#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command to list macros which are defined in more than one UTL file.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from collections import defaultdict

from django.core.management.base import BaseCommand

from utl_files.models import UTLFile, MacroDefinition


def create_defdict(some_type):
    """Return a function which constructs a
    :py:class:`collections.defaultdict` whose default is
    `some_type`. Can be used to create a `defaultdict` whose values
    are `defaultdict` instances.

    """
    return lambda: defaultdict(some_type)


# pylint:disable=no-member
def print_dup_macro_defns():
    """Prints a report of macro names which are defined more than once in
    the UTL files in the database.

    """
    definitions = defaultdict(create_defdict(int))

    for utl_file in UTLFile.objects.all():
        for macro_def in MacroDefinition.objects.filter(source=utl_file):
            definitions[utl_file][macro_def.name] += 1

    # TODO: needs better formatting, line up columns and headers
    print("UTL Files defining a macro more than once:\n")

    found_dups = []
    for utl_file in definitions:
        for macro_name in definitions[utl_file]:
            if definitions[utl_file][macro_name] > 1:
                found_dups.append((utl_file.pkg.name, utl_file.pkg.version,
                                   utl_file.file_path, macro_name,
                                   definitions[utl_file][macro_name], ))

    pkg_width = version_width = file_width = macro_width = 0
    for pkg_name, pkg_version, file_path, macro_name, _ in found_dups:
        pkg_width = max(pkg_width, len(pkg_name))
        version_width = max(version_width, len(pkg_version))
        file_width = max(file_width, len(file_path))
        macro_width = max(macro_width, len(macro_name))

    print("{:{pw}} {:{vw}} {:{fw}} {:{mw}} {}"
          "".format("Package", "Version", "File", "Macro Name", "Times Defined",
                    pw=pkg_width, vw=version_width, fw=file_width, mw=macro_width))
    print("-" * (pkg_width + version_width + file_width + macro_width + 17))

    for pkg_name, pkg_version, file_path, macro_name, defn_count in found_dups:
        print("{:{pw}} {:{vw}} {:{fw}} {:{mw}} {}"
              "".format(pkg_name, pkg_version, file_path,
                        macro_name, defn_count,
                        pw=pkg_width, vw=version_width, fw=file_width, mw=macro_width))


class Command(BaseCommand):
    """Print duplicate macro definition report."""
    help = 'Searches for UTL files that define a macro of the same name more than once.'

    def handle(self, *args, **options):
        print_dup_macro_defns()
