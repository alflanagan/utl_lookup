"""Classes to model UTL files in a Townnews site, including file organization."""

from pathlib import Path
from django.db import models
from django.utils.log import logging

from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_parse_handler import UTLParseError
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.macro_xref import UTLMacroXref, UTLMacro

from papers.models import TNSite
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


class Package(models.Model):
    """A Townnews module that includes files classified as includes, resources, or templates.

    Some packages are TN 'certified' and should always have the same content for a given name
    and version. Packages can be customized on a site-by-site basis and these may contain some
    portion of custom code.

    Packages are always part of an Application (counting "Global" as an app).
    """
    name = models.CharField(max_length=250,
                            help_text="TownNews name for this package.")
    version = models.CharField(max_length=20,
                               help_text="Version number for the package as a whole.")
    is_certified = models.BooleanField(help_text="Is officially certified/supported by TownNews.")
    app = models.ForeignKey(Application,
                            help_text="The application to which this package belongs (or 'Global')")

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ["name", "version"]

    def __str__(self):
        return "{}/{}/{}".format(self.app, self.name, self.version)

    @classmethod
    def _get_props(cls, directory):
        """Helper method; load package properties from `directory`, return as :py:class:`dict`."""
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
    def load_from(cls, directory):
        """Loads a Townnews package from a directory (and subdirectories)."""
        props = cls._get_props(directory)

        application, _ = Application.objects.get_or_create(name=props["app"])

        certified = Path(directory, '.certification').exists()

        if Package.objects.filter(name=props["name"], version=props["version"]).exists():
            # TODO: handle replacing existing package
            raise PackageError("Package '{}', version '{}' is already loaded.\n To load again,"
                               " first remove the existing package from the data."
                               "".format(props["name"], props["version"]))

        new_pkg = cls(name=props["name"], version=props["version"], is_certified=certified,
                      app=application)
        new_pkg.save()
        for key in props:
            if key not in ["name", "version", "app"]:
                # doesn't exist since we just created package
                new_prop = PackageProp(pkg=new_pkg, key=key, value=props[key])
                new_prop.save()

        deps = {}
        with Path(directory, 'package/dependencies.ini').open() as depin:
            for line in depin:
                key, value = line[:-1].split('=')
                deps[key] = value.replace('"', '')
        for key in deps:
            new_dep = PackageDep(pkg=new_pkg, dep_name=key, dep_version=deps[key])
            try:
                new_dep.dep_pkg = Package.objects.get(name=key, version=deps[key])
            except Package.DoesNotExist:
                pass
            new_dep.save()

        new_pkg.get_utl_files(directory)

        return new_pkg

    def get_utl_files(self, directory):
        """Scans `directory` and its children for files with a '.utl' extension; adds them to
        the database as :py:class:`~utl_files.models.UTLFile` objects and sets this instance as
        their package.

        """
        if not isinstance(directory, Path):
            directory = Path(directory)

        filenames = directory.glob('**/*.utl')
        for filename in filenames:
            UTLFile.create_from(filename, self)


class PackageProp(models.Model):
    """Properties for a package. Any key-value pair except those that have their own field in
    :py:class:`utl_files.models.Package`.

    """
    pkg = models.ForeignKey(Package)
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ("pkg", "key")
        verbose_name = "package property"
        verbose_name_plural = "package properties"

    def __str__(self):
        return "{}: {}".format(self.key, self.value)


class PackageDep(models.Model):
    """Dependency for a Townnews Package. Each dependency consists of a package name and a
    version.

    """
    pkg = models.ForeignKey(Package,
                            help_text="The package which has this dependency")
    dep_name = models.CharField(max_length=200, blank=False,
                                help_text="The name of the required package")
    dep_pkg = models.ForeignKey(Package, null=True,  # may be Null if package not in db.
                                related_name="dep_pkg",
                                help_text="The full data on the required package (opt.)")
    dep_version = models.CharField(max_length=50, blank=False,
                                   help_text="The specific version required.")

    class Meta:  # pylint: disable=missing-docstring
        # one version of a package is dependent on at most one version of another package
        unique_together = ("pkg", "dep_name")
        verbose_name = "package dependency"
        verbose_name_plural = "package dependencies"

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
        max_length=1024,
        help_text='The file path, relative to the package base directory.')
    pkg = models.ForeignKey(Package)

    # instantiate parser once -- it's big
    handler = UTLParseHandlerAST(exception_on_error=True)
    parser = UTLParser([handler])

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ("pkg", "file_path")
        verbose_name = "UTL File"

    def __str__(self):
        return "{}/{}:{}".format(self.pkg.app, self.pkg.name, self.file_path)

    # TODO: move this to a custom manager
    @classmethod
    def create_from(cls, filename, package):
        """Creates and returns a new :py:class:`utl_files.models.UTLFile` instance containing
        information about the file `filename` and designating `package` as the containing
        package.

        :param pathlib.Path filename: The filename of .utl file.

        :param utl_files.models.Package package: A UTL package to which the file belongs.

        """
        new_file = cls(file_path=str(filename), pkg=package)
        new_file.full_clean()
        new_file.save()
        new_file.get_macros()

    def get_macros(self):
        """Load the given UTL file and add information about macro definitions and references to
        the database.

        """
        path = Path(self.file_path)
        with path.open() as utlin:
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
            new_macro = MacroDefinition(name=macro.name, source=self, text=text, start=macro.start,
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
                               help_text="The file where the macro is defined.")
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


class MacroRef(models.Model):
    """Records a macro call in a specific UTL file."""
    source = models.ForeignKey(UTLFile)
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
        return '{}:{} - {}'.format(self.line, self.start, self.text[:100])
