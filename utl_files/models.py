"""Classes to model UTL files in a Townnews site, including file organization."""

import os
import json
from pathlib import Path

from django.db import models
from django.utils.log import logging

from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_parse_handler import UTLParseError
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.macro_xref import UTLMacroXref, UTLMacro
from utl_lib.tn_package import TNPackage

from papers.models import TownnewsSite

# pylint: disable=W0232,R0903,E1101


class PackageError(Exception):
    "Catchall for exceptions raised by Package class"
    pass


class UTLFileError(PackageError):
    """General error with a UTLFile object."""
    pass


class UTLFileImportError(UTLFileError):
    """Exception raised when a fatal error occurs during import of an
    :py:class:`~utl_files.models.UTLFile` file.

    """
    pass


class Application(models.Model):
    """A Townnews application, or group of related functionality."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:  # pylint: disable=missing-docstring
        ordering = ['name']

    def __str__(self):
        return self.name

    def to_dict(self):
        """Write record attributes to a dictionary, for easy conversion to JSON."""
        return {"id": self.pk,
                "name": self.name}


class Package(models.Model):
    """A Townnews package is a collection of files implementing functionality for a
    :py:class:`TownnewsSite`.

    There are four types of packages: *global skins* contain customized files for a particular
    site. *skins* are bundles of functionality for a specific application. *components* are
    collections of macros for use by other packages. *blocks* are templates and associated files
    for a specific block type.

    Packages (except global skins) may be "certified" by Townnews: this means they contain only
    the files and code provided by Townnews, and therefore can be supported by them. Packages
    which are customized in some way are no longer "certified", and qualify for a lower level of
    support.

    This model contains fields for all the package types. Some fields don't apply to all types.

    """
    # Would prefer to have an abstract AbstractPackage model, then concrete tables for each type
    # with fields specific to that type. However, foreign keys can't point to an abstract model.
    #
    # One problem is that unique key for certified pkgs is name + version, but unique key for
    # customized packages is site + name + download date/time (note TN IDE doesn't enforce
    # bumping version number on change, and global skins don't have version)
    name = models.CharField(max_length=250,
                            help_text="TownNews name for this package.")
    version = models.CharField(max_length=20, blank=True,  # global skins have no version
                               help_text="Version number for the package as a whole.")
    is_certified = models.BooleanField(help_text="Is officially certified/supported by TownNews.")
    # Skins belong to an app, and blocks can have a "block type" which is basically an app reference
    # global skins and components don't have an application.
    app = models.ForeignKey(Application,
                            on_delete=models.CASCADE,
                            help_text="The application to which this package belongs",
                            null=True)
    last_download = models.DateTimeField(help_text="When this package's ZIP file was downloaded.")
    disk_directory = models.FilePathField(allow_files=False, allow_folders=True, blank=True,
                                          help_text="The location of the package's files on disk, "
                                          "relative to some common root directory.")
    site = models.ForeignKey(TownnewsSite, null=True,
                             help_text="For customized packages, the site that 'owns' the "
                             "customizations.")

    PACKAGE_CHOICES = (
        (TNPackage.GLOBAL_SKIN, "global skin"),
        (TNPackage.SKIN, "application skin"),
        (TNPackage.BLOCK, "block"),
        (TNPackage.COMPONENT, "component"),
    )
    pkg_type = models.CharField(max_length=1,
                                choices=PACKAGE_CHOICES)

    def __str__(self):
        return "{}/{}/{}".format(self.app, self.name, self.version)

    def to_dict(self):
        """Write record attributes to a dictionary, for easy conversion to JSON."""
        return {"id": self.pk,
                "app": self.app,
                "name": self.name,
                "version": self.version,
                "is_certified": "y" if self.is_certified else "n"}

    @classmethod
    def _get_props(cls, directory):
        """Helper method; load package properties from `directory`, return as :py:class:`dict`."""
        # would be better to do this in PackageProp, but I need property values before creating
        # Package object, and I can't create PackageProp objects until after
        if not isinstance(directory, Path):
            directory = Path(directory)
        props = {}
        # known config properties are:
        # apparently required: block_types capabilities name title type version
        # optional: app
        with (directory / 'package/config.ini').open() as propin:
            for line in propin:
                key, value = line[:-1].split('=')
                props[key] = value[1:-1]

        if "app" not in props:
            props["app"] = "Global"
        return props

    @classmethod
    def load_from(cls, directory: Path, site: TownnewsSite, pkg_type: str) -> "Package":
        """Loads a Townnews package from a directory (and subdirectories)."""
        if pkg_type not in [pkg_type for pkg_type, _ in TNPackage.PACKAGE_TYPES]:
            raise ValueError("pkg_type must be one of the symbolic constants defined in TNPackage")

        new_pkg = TNPackage.load_from(directory, "")
        my_pkg = Package(name=new_pkg.name,
                         version=new_pkg.version,
                         is_certified=new_pkg.is_certified,
                         app=new_pkg.app,
                         # last_download=new_pkg.
                         # disk_directory=new_pkg.
                         site=site,
                         pkg_type=pkg_type)
        my_pkg.clean()
        my_pkg.save()

    def get_utl_files(self, root_dir):
        """Prefixes `root_dir` to `self.disk_directory`, scans that directory for files with a
        '.utl' extension; adds them to the database as :py:class:`~utl_files.models.UTLFile`
        objects and sets this instance as their package.

        """
        if not isinstance(root_dir, Path):
            root_dir = Path(root_dir)

        disk_dir = root_dir / self.disk_directory
        if not disk_dir.is_dir():
            raise PackageError("Can't find package at {}.".format(disk_dir))
        filenames = disk_dir.glob('**/*.utl')
        for filename in filenames:
            UTLFile.create_from(filename, root_dir, self)


class PackageProp(models.Model):
    """Properties for a package. Any key-value pair except those that have their own field in
    :py:class:`utl_files.models.Package`.

    """
    pkg = models.ForeignKey(Package, on_delete=models.CASCADE)
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ("pkg", "key")
        verbose_name = "package property"
        verbose_name_plural = "package properties"

    def __str__(self):
        return "{}: {}".format(self.key, self.value)

    def to_dict(self):
        """Write record attributes to a dictionary, for easy conversion to JSON."""
        return {"id": self.pk,
                "name": self.pkg.name,
                "version": self.pkg.version,
                "key": self.key,
                "value": self.value}


class PackageDep(models.Model):
    """Dependency for a Townnews Package. Each dependency consists of a package name and a
    version.

    """
    pkg = models.ForeignKey(Package,
                            help_text="The package which has this dependency",
                            on_delete=models.CASCADE)
    dep_name = models.CharField(max_length=200, blank=False,
                                help_text="The name of the required package")
    dep_pkg = models.ForeignKey(Package, null=True,  # may be Null if package not in db.
                                related_name="dep_pkg",
                                help_text="The full data on the required package (opt.)",
                                on_delete=models.CASCADE)
    dep_version = models.CharField(max_length=50, blank=False,
                                   help_text="The specific version required.")

    class Meta:  # pylint: disable=missing-docstring
        # one version of a package is dependent on at most one version of another package
        unique_together = ("pkg", "dep_name")
        verbose_name = "package dependency"
        verbose_name_plural = "package dependencies"

    def to_dict(self):
        """Write record attributes to a dictionary, for easy conversion to JSON."""
        return {"id": self.pk,
                "name": self.pkg.name,
                "version": self.pkg.version,
                "dep_name": self.dep_name,
                "dep_version": self.dep_version}

    def __str__(self):
        return "{} depends on {} ({})".format(self.pkg, self.dep_name, self.dep_version)

    def check_for_deps(self):
        """Looks for dependencies which don't have pointer to Package table. For each, checks
        whether dependency exists and if found, adds it to the dep_pkg field.

        """
        for dep in PackageDep.objects.filter(dep_pkg=None):
            # only look for certified packages for now. Handling of custom packages needs to be
            # redone (FIXME).
            dep_pkg = Package.objects.filter(name=self.dep_name, version=self.dep_version,
                                             is_certified=True)
            if dep_pkg:
                dep.dep_pkg = dep_pkg
                dep.save()


class UTLFile(models.Model):
    """Reference information regarding a specific file in the UTL templates directories."""
    file = models.FileField(upload_to='utl_files', null=True, blank=True)
    file_path = models.FilePathField(
        allow_folders=False,
        max_length=2048,
        help_text='The file path, relative to the package base directory.')
    pkg_directory = models.CharField(
        max_length=1024,
        help_text='The package base directory on the hard drive.'
    )
    pkg = models.ForeignKey(Package, on_delete=models.CASCADE)

    # instantiate parser once -- it's big
    handler = UTLParseHandlerAST(exception_on_error=True)
    parser = UTLParser([handler])

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ("pkg", "file_path")
        verbose_name = "UTL File"

    def __str__(self):
        return "{}/{}:{}".format(self.pkg.app, self.pkg.name, self.file_path)

    def to_dict(self):
        """Write record attributes to a dictionary, for easy conversion to JSON."""
        return {"id": self.pk,
                "path": self.file_path,
                "name": self.pkg.name,
                "pkg_directory": self.pkg_directory,
                "version": self.pkg.version}

    @property
    def base_filename(self):
        """Returns just he base filename part of :py:attr:`utl_files.models.UTLFile.file_path`."""
        return os.path.basename(self.file_path)

    @property
    def full_file_path(self):
        """The full path of the file, including the package directory."""
        return Path(self.pkg_directory).joinpath(self.file_path)

    # TODO: move this to a custom manager
    @classmethod
    def create_from(cls, filename, package_directory, package):
        """Creates and returns a new :py:class:`utl_files.models.UTLFile` instance containing
        information about the file `filename` and designating `package` as the containing
        package.

        :param pathlib.Path filename: The filename of .utl file.

        :param utl_files.models.Package package: A UTL package to which the file belongs.

        """
        new_file = cls(file_path=str(filename.relative_to(package_directory)),
                       pkg_directory=package_directory,
                       pkg=package)
        new_file.full_clean()
        new_file.save()
        new_file.get_macros()

    def get_macros(self):
        """Load the given UTL file and add information about macro definitions and references to
        the database.

        """
        with self.full_file_path.open() as utlin:
            text = utlin.read()

        if not text:
            # file was empty. Nothing to do
            return

        self.parser.restart()  # existing handlers are OK, don't store state
        try:
            utldoc = self.parser.parse(text, filename=self.file_path)
        except UTLParseError as upe:
            logging.error(" parsing '{}': {}".format(self.file_path, upe))
            return

        if utldoc is None:
            logging.error(" parsing '{}': returned None.".format(self.file_path))

        xref = UTLMacroXref(utldoc, text)
        for macro in xref.macros:
            isinstance(macro, UTLMacro)
            new_macro = MacroDefinition(name=macro.name, source=self,
                                        text=text[macro.start:macro.end], start=macro.start,
                                        end=macro.end, line=macro.line)
            new_macro.full_clean()
            new_macro.save()

        for ref in xref.references:

            new_ref = MacroRef(macro_name=ref["macro"],
                               source=self,
                               start=ref["start"],
                               line=ref["line"],
                               text=ref["call_text"])
            new_ref.full_clean()
            new_ref.save()


class MacroDefinition(models.Model):
    """Reference information for a macro definition in a specific UTL file."""
    source = models.ForeignKey(UTLFile,
                               help_text="The file where the macro is defined.",
                               on_delete=models.CASCADE)
    text = models.TextField(max_length=50000)
    name = models.CharField(max_length=250)
    start = models.IntegerField(
        null=True,
        help_text="Character offset in file at which macro defintion starts.")
    end = models.IntegerField(
        null=True,
        help_text="Character offset in file at which macro definition ends."
    )
    line = models.IntegerField(
        null=True,
        help_text="Line number of macro definition in file."
    )

    class Meta:  # pylint: disable=C0111
        # source and name are NOT unique; legal to redefine macro in a file
        unique_together = ("source", "start")

    def __str__(self):
        return "{}() [{:,}]".format(self.name, self.line)

    def to_dict(self):
        """Return a dictionary from values of model attributes, suitable for serialization."""
        return {"id": self.pk,
                "pkg": self.source.pkg.name,
                "pkg_version": self.source.pkg.version,
                "file": self.source.file_path,
                "name": self.name,
                "start": self.start,
                "end": self.end,
                "line": self.line}


class MacroRef(models.Model):
    """Records a macro call in a specific UTL file."""
    source = models.ForeignKey(UTLFile, on_delete=models.CASCADE)
    start = models.IntegerField(
        help_text="Character offset in source file of first character of macro call.")
    line = models.IntegerField(
        null=True,
        help_text="Line number of macro call in file.")
    text = models.CharField(
        max_length=4000,
        help_text="The actual text of the macro call, with args.")
    macro_name = models.CharField(
        max_length=4000,
        help_text="The ID or expression identifying the macro to be called.")

    class Meta:  # pylint: disable=C0111
        # can't use source, start alone as unique because, e.g.,
        # articleItem.items('type':'image')[0].preview([300])
        # is two macro calls
        unique_together = ("source", "start", "macro_name")

    def __str__(self):
        # because pylint doesn't understand that instance 'text' is str, not CharField
        # pylint: disable=unsubscriptable-object
        return '{}:{} - {}'.format(self.line, self.start, self.text[:100])

    def to_dict(self):
        """Write record attributes to a dictionary, for easy conversion to JSON."""
        return {"id": self.pk,
                "pkg": self.source.pkg.name,
                "pkg_version": self.source.pkg.version,
                "file": self.source.file_path,
                "line": self.line,
                "text": self.text,
                "name": self.macro_name}


class UTLFilesJsonEncoder(json.JSONEncoder):
    """Provide ability to encode to JSON for each model class.

    (Actually will work for any object that implements to_dict() method returning a JSON-dumpable
    dictionary.)

    """

    def default(self, o):  # pylint: disable=E0202
        try:
            return o.to_dict()
        except AttributeError:
            return json.JSONEncoder.default(self, o)
