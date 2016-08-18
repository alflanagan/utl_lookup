"""Classes to model UTL files in a Townnews site, including file organization."""

import os
import re
import time
import json
from pathlib import Path
from warnings import warn

from django.db import models
from django.utils.log import logging
from django.conf import settings
from django.core.exceptions import ValidationError

from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_parse_handler import UTLParseError
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.macro_xref import UTLMacroXref
from utl_lib.tn_package import TNPackage
from utl_lib.tn_site import TNSiteMeta

from papers.models import TownnewsSite, TownnewsSiteMetaData

from utl_files.code_markup import UTLWithMarkup
# pylint: disable=W0232,R0903,E1101


class PackageError(Exception):
    """Catchall for exceptions raised by Package class"""
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
        return {"id": self.pk, "name": self.name}


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
    name = models.CharField(max_length=250, help_text="TownNews name for this package.")
    version = models.CharField(max_length=20, blank=True,  # global skins have no version
                               help_text="Version number for the package as a whole.")
    is_certified = models.BooleanField(help_text="Is officially certified/supported by TownNews.")
    # Skins belong to an app, and blocks can have a "block type" which is basically an app reference
    # global skins and components don't have an application.
    app = models.ForeignKey(Application,
                            on_delete=models.CASCADE,
                            help_text="The application to which this package belongs",
                            blank=True,
                            null=True)
    # TODO: get download date from .certification for certified files
    last_download = models.DateTimeField(help_text="When this package's ZIP file was downloaded.",
                                         null=True,
                                         blank=True)
    disk_directory = models.FilePathField(max_length=4096,
                                          allow_files=False,
                                          allow_folders=True,
                                          blank=True,
                                          help_text="The location of the package's files on disk, "
                                          "relative to some common root directory.")
    site = models.ForeignKey(TownnewsSite,
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE,
                             help_text="For customized packages, the site that 'owns' the "
                             "customizations.")

    # copy attributes from TNPackage for convenience
    GLOBAL_SKIN = TNPackage.GLOBAL_SKIN
    SKIN = TNPackage.SKIN
    BLOCK = TNPackage.BLOCK
    COMPONENT = TNPackage.COMPONENT

    PACKAGE_CHOICES = ((TNPackage.GLOBAL_SKIN, "global skin"),
                       (TNPackage.SKIN, "application skin"),
                       (TNPackage.BLOCK, "block"),
                       (TNPackage.COMPONENT, "component"), )
    pkg_type = models.CharField(max_length=1, choices=PACKAGE_CHOICES)

    # override
    def validate_unique(self, exclude=None):
        """
        Checks unique constraints on the model and raises ``ValidationError`` if any failed. A
        certified package is unique on just [name, version]; a customized package is unique on
        [site, last_download, name].
        """
        # unfortunately we're now assuming that validation_unique will use error_list property,
        # not error_dict. if that changes we have a problem...
        error_list = []
        code = None
        params = None
        try:  # pragma: no cover
            super().validate_unique(exclude)
        except ValidationError as verr:  # pragma: no cover
            error_list.extend(verr.error_list)
            code = verr.code
            params = verr.params

        if "is_certified" not in exclude:
            if self.is_certified:
                if "name" not in exclude and "version" not in exclude:
                    if Package.objects.filter(name=self.name, version=self.version).exists():
                        error_list.append("Unique constraint violation: certified package '{}', "
                                          "version {} is already in the database."
                                          "".format(self.name, self.version))
            else:
                if not set(["site", "last_download", "name"]).intersection(set(exclude)):
                    if self.last_download is None:
                        error_list.append("Package '{}' is not certified but has no downloaded"
                                          " time.".format(self.name))
                    if self.site is None:
                        error_list.append("Package '{}' is not certified but site not specified."
                                          "".format(self.name))
                    if Package.objects.filter(name=self.name,
                                              site=self.site,
                                              last_download=self.last_download).exists():
                        error_list.append("Unique constraint violation: package '{}' customized"
                                          " for site '{}' dated {} is already in the database."
                                          "".format(self.name, self.site.name, self.last_download))
        if error_list:
            raise ValidationError(error_list, code, params)

    def __str__(self):
        if self.is_certified:
            if self.app.name == 'global':
                return "certified/{}/{}".format(self.name, self.version)
            else:
                return "certified/{}::{}/{}".format(self.app, self.name, self.version)
        else:
            if self.app.name == 'global':
                return "{}/{}({})".format(self.site, self.name,
                                          self.last_download.strftime('%Y-%m-%d %H:%M'))
            else:
                return "{}/{}::{}({})".format(self.site, self.app, self.name,
                                              self.last_download.strftime('%Y-%m-%d %H:%M'))

    def to_dict(self):
        """Write record attributes to a dictionary, for easy conversion to JSON."""
        # need to be sure we have natural keys for each foreign key
        return {"id": self.pk,
                # Application (name)
                "app": self.app.name,
                # TownnewsSite: (URL)
                "site": self.site.URL if self.site else None,
                "name": self.name,
                "version": self.version,
                "is_certified": "y" if self.is_certified else "n",
                "downloaded": self.last_download,
                "pkg_type": self.pkg_type,
                "location": self.disk_directory, }

    def add_keys_to_dict(self, fields):
        """Adds a set of keys which allow caller to retrieve this record to a
        dictionary `fields`.

        Classes that have a Package foreign key can call this method to add
        all the fields that may make up the key.

        """
        fields.update({
            # Package: (name, version) OR (name, site, last_download)
            "pkg_name": self.name,
            "pkg_version": self.version,
            "pkg_site": self.site.URL if self.site else None,
            "pkg_download": self.last_download,
            # not part of foreign key but tells caller which fields to use
            "pkg_certified": self.is_certified})
        return fields

    @classmethod
    def load_from(cls, directory: Path, site: TownnewsSite, pkg_type: str) -> "Package":
        """Loads a Townnews package from a directory (and subdirectories)."""
        if pkg_type not in [pkg_type for pkg_type, _ in TNPackage.PACKAGE_TYPES]:
            raise ValueError("pkg_type must be one of the symbolic constants defined in TNPackage")

        new_pkg = TNPackage.load_from(directory, "")
        isinstance(site, TownnewsSite)
        last_download = None
        if not new_pkg.is_certified:
            meta_path = Path(settings.TNPACKAGE_FILES_ROOT) / site.domain
            custom_meta = TNSiteMeta(site.name, meta_path)
            if not custom_meta.loaded:
                warn("Failed to find meta data for {} at {}.".format(site.URL, meta_path))
            if (new_pkg.name in custom_meta.data and
                    "last_download" in custom_meta.data[new_pkg.name]):
                # Path(fname).stat().st_ctime is giving us UTC
                # make it a structure
                last_download = time.gmtime(custom_meta.data[new_pkg.name]["last_download"])
                # YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
                # make it a timezone-aware string
                last_download = time.strftime('%Y-%m-%d %H:%M:%SZ', last_download)

        if last_download is None:
            # well, site_meta was a bust. Try the old-fashioned way.
            last_download = time.gmtime(directory.stat().st_mtime)
            last_download = time.strftime('%Y-%m-%d %H:%M:%SZ', last_download)

        try:
            app = Application.objects.get(name=new_pkg.app)
        except Application.DoesNotExist:
            # much better error message than original
            raise UTLFileImportError("Application type '{}' not found.".format(new_pkg.app))

        directory = directory.relative_to(settings.TNPACKAGE_FILES_ROOT)

        my_pkg = Package(name=new_pkg.name,
                         version=new_pkg.version,
                         is_certified=new_pkg.is_certified,
                         app=app,
                         last_download=last_download,
                         disk_directory=str(directory),
                         site=site,
                         pkg_type=pkg_type)
        my_pkg.full_clean()
        my_pkg.save()
        my_pkg.get_utl_files()
        try:
            PackageProp.from_package_metadata(my_pkg)
            PackageDep.from_package_metadata(my_pkg)
        except FileNotFoundError:
            warn("Skipping import of data from .metadata/.meta.json, file not found")
        return my_pkg

    def get_utl_files(self):
        """Scans the disk directory for files with a '.utl' extension; adds them to the database
        as :py:class:`~utl_files.models.UTLFile` objects and sets this instance as their
        package.

        """
        disk_dir = Path(settings.TNPACKAGE_FILES_ROOT) / self.disk_directory
        if not disk_dir.is_dir():
            raise PackageError("Can't find package at {}.".format(disk_dir))
        filenames = disk_dir.glob('**/*.utl')
        for filename in filenames:
            new_file = UTLFile.create_from(filename, self)
            new_file.full_clean()
            new_file.save()

    @classmethod
    def find_packages_for(cls, site, pkg_name):
        """Checks metadata for a site and finds packages with a given name.

        :param [str, TownnewsSite] site: A TownnewsSite instance, or its URL.

        :param str pkg_name: the name of a package to look for.

        :returns: Generator object yielding Package instances.

        """
        if isinstance(site, str):
            site = TownnewsSite.objects.get(URL=site)

        mdata = TownnewsSiteMetaData.objects.filter(site=site, pkg_name=pkg_name)
        for mdatum in mdata:
            try:
                pkg = cls.objects.get(name=pkg_name, version=mdatum.version,
                                      is_certified=True)
                yield pkg
            except cls.DoesNotExist:
                pass


class PackageProp(models.Model):
    """Properties for a package. Any key-value pair except those that have their own field in
    :py:class:`utl_files.models.Package`.

    """
    pkg = models.ForeignKey(Package, on_delete=models.CASCADE)
    key = models.CharField(max_length=50)
    value = models.TextField()

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ("pkg", "key")
        verbose_name = "package property"
        verbose_name_plural = "package properties"

    def __str__(self):
        return "{}: {}".format(self.key, self.value)

    def to_dict(self):
        """Write record attributes to a dictionary, for easy conversion to JSON."""
        my_fields = {"id": self.pk, "key": self.key, "value": self.value}
        # get foreign key fields from pkg
        self.pkg.add_keys_to_dict(my_fields)
        return my_fields

    @classmethod
    def from_package_metadata(cls, package: Package):
        """Reads the ``.metadata/.meta.json`` file for :py:class:`~utl_files.models.Package`
        object package and creates appropriate PackageProp instances.

        :raises: NotFoundError if package is not present at package.disk_directory, if there is
            no ``.meta.json`` file.

        """
        meta_file = (Path(settings.TNPACKAGE_FILES_ROOT) / Path(package.disk_directory) /
                     Path('.metadata/.meta.json'))
        with meta_file.open('r') as meta_in:
            data = json.load(meta_in)
        for key in data:
            # key "dependencies" is handled in PackageDep
            if key != "dependencies" and data[key] is not None and data[key] != '':
                new_prop = PackageProp(pkg=package, key=key, value=data[key])
                try:
                    new_prop.full_clean()
                except:  # pragma: nocover
                    print("Key is '{}', value is '{}'.".format(key, data[key]))
                    raise
                new_prop.save()


class PackageDep(models.Model):
    """Dependency for a Townnews Package. Each dependency consists of a package name and a
    version.

    """
    # Database best practice would probably be to have two tables, one relating two packages and
    # the other relating a package to a name/version pair. Easier to get primary key right that
    # way. But you'd have to check for duplication between tables.
    pkg = models.ForeignKey(Package,
                            help_text="The package which has this dependency",
                            on_delete=models.CASCADE)
    dep_name = models.CharField(max_length=200,
                                blank=True,
                                help_text="The name of the required package")
    dep_pkg = models.ForeignKey(Package, null=True,  # may be Null if package not in db.
                                blank=True,
                                related_name="dep_pkg",
                                help_text="The full data on the required package (opt.)",
                                on_delete=models.CASCADE)
    dep_version = models.CharField(max_length=50,
                                   blank=True,
                                   help_text="The specific version required.")

    class Meta:  # pylint: disable=missing-docstring
        verbose_name = "package dependency"
        verbose_name_plural = "package dependencies"

    def to_dict(self):
        """Write record attributes to a dictionary, for easy conversion to JSON."""
        my_fields = {"id": self.pk,
                     "dep_name": self.dep_name,
                     "dep_version": self.dep_version}
        return self.pkg.add_keys_to_dict(my_fields)

    def __str__(self):
        str_fmt = "{} depends on {} ({})"
        if self.dep_pkg:
            return str_fmt.format(self.pkg, self.dep_pkg.name, self.dep_pkg.version)
        else:
            return str_fmt.format(self.pkg, self.dep_name, self.dep_version)

    @staticmethod
    def check_for_deps():
        """Looks for dependencies which don't have pointer to Package table. For each, checks
        whether dependency exists and if found, adds it to the dep_pkg field.

        """
        for dep in PackageDep.objects.filter(dep_pkg=None):
            try:
                dep_pkg = Package.objects.get(name=dep.dep_name,
                                              version=dep.dep_version,
                                              is_certified=True)
            except Package.DoesNotExist:
                continue
            dep.dep_pkg = dep_pkg
            dep.save()

    # override
    def validate_unique(self, exclude=None):
        """Verifies uniqueness constraint on the record. Either the combination (pkg, dep_pkg)
        is unique, or the combination (pkg, dep_name, dep_version) is unique.

        This allows us to specify a dependency on a package not present in the database.

        """
        super().validate_unique(exclude)
        if self.dep_pkg is not None:
            if PackageDep.objects.filter(pkg=self.pkg, dep_pkg=self.dep_pkg).exists():
                raise ValidationError("PackageDep object with duplicate (pkg, dep_pkg) combination"
                                      " (dep_pkg not null)")
        else:
            if PackageDep.objects.filter(pkg=self.pkg,
                                         dep_name=self.dep_name,
                                         dep_version=self.dep_version).exists():
                raise ValidationError("PackageDep object with duplicate (pkg, dep_name, "
                                      "dep_version) combination (dep_pkg is null)")

    @classmethod
    def from_package_metadata(cls, package: Package):
        """Reads the ``.metadata/.meta.json`` file for :py:class:`~utl_files.models.Package`
        object package and creates appropriate PackageDep instances.

        :raises: NotFoundError if package is not present at package.disk_directory, if there is
            no ``.meta.json`` file.

        """
        meta_file = (Path(settings.TNPACKAGE_FILES_ROOT) / Path(package.disk_directory) /
                     Path('.metadata/.meta.json'))
        with meta_file.open('r') as meta_in:
            data = json.load(meta_in)
        if "dependencies" in data:
            deps = data["dependencies"]
            for pkg_name in deps:
                this_dep_pkg = None
                pkg_version = deps[pkg_name]
                if Package.objects.filter(name=pkg_name,
                                          version=pkg_version,
                                          is_certified=True).exists():
                    this_dep_pkg = Package.objects.filter(name=pkg_name,
                                                          version=pkg_version,
                                                          is_certified=True).first()
                elif (not package.is_certified and
                      Package.objects.filter(name=pkg_name,
                                             version=pkg_version,
                                             site=package.site).exists()):
                    this_dep_pkg = Package.objects.filter(name=pkg_name,
                                                          version=pkg_version,
                                                          site=package.site).first()
                if this_dep_pkg:
                    new_dep = PackageDep(pkg=package, dep_pkg=this_dep_pkg)
                else:
                    new_dep = PackageDep(pkg=package, dep_name=pkg_name,
                                         dep_version=deps[pkg_name])
                new_dep.full_clean()
                new_dep.save()


class UTLFile(models.Model):
    """Reference information regarding a specific file in the UTL templates directories."""
    file_path = models.FilePathField(
        allow_folders=False,
        max_length=2048,
        help_text='The file path, relative to the package base directory.')
    pkg = models.ForeignKey(Package, on_delete=models.CASCADE)
    file_text = models.TextField(blank=True, help_text="Source code from UTL file.")

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
        my_fields = {"id": self.pk, "path": self.file_path, "text": self.file_text}
        return self.pkg.add_keys_to_dict(my_fields)

    @property
    def base_filename(self):
        """Returns just he base filename part of :py:attr:`utl_files.models.UTLFile.file_path`."""
        return os.path.basename(self.file_path)

    @property
    def full_file_path(self):
        """The full path of the file, including the package directory."""
        return Path(settings.TNPACKAGE_FILES_ROOT) / Path(self.pkg.disk_directory) / self.file_path

    @classmethod
    def create_from(cls, filename, package):
        """Creates and returns a new :py:class:`utl_files.models.UTLFile` instance.

        :param pathlib.Path filename: The filename of .utl file.

        :param utl_files.models.Package package: A UTL package to which the file belongs.

        """
        new_file = cls(file_path=str(filename.relative_to(Path(settings.TNPACKAGE_FILES_ROOT) /
                                                          package.disk_directory)),
                       pkg=package)
        if new_file.full_file_path.exists():
            with new_file.full_file_path.open("r") as srcin:
                new_file.file_text = srcin.read()
        new_file.full_clean()
        new_file.save()
        new_file.get_macros()
        return new_file

    def get_macros(self):
        """Add information about macro definitions and references to the database.

        """
        if not self.file_text:
            with self.full_file_path.open() as utlin:
                self.file_text = utlin.read()

        if self.file_text:
            self.parser.restart()  # existing handlers are OK, don't store state
            try:
                utldoc = self.parser.parse(self.file_text, filename=self.file_path)
            except UTLParseError as upe:
                logging.error(" parsing '{}': {}".format(self.file_path, upe))
                return

            # not sure if None value is possible
            if utldoc is None:  # pragma: no cover
                logging.error(" parsing '{}': returned None.".format(self.file_path))

            xref = UTLMacroXref(utldoc, self.file_text)
            for macro in xref.macros:
                new_macro = MacroDefinition(name=macro.name,
                                            source=self,
                                            text=self.file_text[macro.start:macro.end],
                                            start=macro.start,
                                            end=macro.end,
                                            line=macro.line)
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

    @property
    def text_with_markup(self):
        """Returns the text of the file, with syntax markup."""
        working = self.file_text.strip()
        twmu = UTLWithMarkup(working)
        return twmu.text


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
    end = models.IntegerField(null=True,
                              help_text="Character offset in file at which macro definition ends.")
    line = models.IntegerField(null=True, help_text="Line number of macro definition in file.")

    WS_BEGIN_RE = re.compile(r'\A\s+')
    "Match whitespace at the beginning of the line"

    SPACES_FOR_TAB = ' ' * 8
    "Number of spaces to replace \t character in text (match Townnews editor)"

    class Meta:  # pylint: disable=C0111
        # source and name are NOT unique; legal to redefine macro in a file
        unique_together = ("source", "start")

    def __str__(self):
        return "{}() [{:,}]".format(self.name, self.line)

    def to_dict(self):
        """Return a dictionary from values of model attributes, suitable for serialization."""
        my_fields = {"id": self.pk,
                     "file": self.source.file_path,
                     "name": self.name,
                     "start": self.start,
                     "end": self.end,
                     "line": self.line}
        the_pkg = self.source.pkg
        return the_pkg.add_keys_to_dict(my_fields)

    def clean(self):
        """Cleans up macro text."""
        self.clean_up_text()

    def clean_up_text(self):
        """Process the macro text. Normalize the macro xxx() line, and trim white extra white
        space off the left and right."""
        working = []
        lines = self.text.split("\n")
        pos = 0
        while not lines[pos].strip():
            pos += 1
        if 'macro' in lines[pos]:
            working.append(lines[pos].strip())
        else:
            # shouldn't happen
            return
        # handle "macro" as the only word on the line
        if working[0] == 'macro':
            try:
                working[0] += " " + lines[pos + 1].strip()
                pos += 2
            except IndexError:
                pass
        else:
            pos += 1
        min_ws_len = 50000000
        for line in lines[pos:]:
            line = line.replace('\t', self.SPACES_FOR_TAB)
            match = self.WS_BEGIN_RE.match(line)
            if match:
                min_ws_len = min([min_ws_len, match.end()])
            elif line.strip():
                # not blank, no whitespace
                min_ws_len = 0
                break  # at minimum already
        for line in lines[pos:]:
            line = line.replace('\t', self.SPACES_FOR_TAB)
            working.append(line[min_ws_len:].rstrip())
        self.text = "\n".join(working)

    @property
    def text_with_markup(self):
        """Returns the text of the macro definition, with syntax markup."""
        # macro def always starts, ends in UTL mode, but when we pulled text
        # we may have dropped enclosing [% %]
        working = self.text.strip()
        if not working.startswith('[%'):
            working = '[% ' + working
        if not working.endswith('%]'):
            working += ' %]'
        twmu = UTLWithMarkup(working)
        return twmu.text


class MacroRef(models.Model):
    """Records a macro call in a specific UTL file."""
    source = models.ForeignKey(UTLFile, on_delete=models.CASCADE)
    start = models.IntegerField(
        help_text="Character offset in source file of first character of macro call.")
    line = models.IntegerField(null=True, help_text="Line number of macro call in file.")
    text = models.CharField(max_length=4000,
                            help_text="The actual text of the macro call, with args.")
    macro_name = models.CharField(
        max_length=4000,
        help_text="The ID or expression identifying the macro to be called.")

    class Meta:  # pylint: disable=C0111
        # can't use source, start alone as unique because, e.g.,
        # we have records like this:
        # start | line |               macro_name                | source_id
        # ------+------+-----------------------------------------+-----------
        #  3179 |   72 | result.items                            | 10283
        #  3179 |   72 | result.items('type':'image')[0].preview | 10283
        # i.e. a macro call can return an object which can be part of another
        # reference
        unique_together = ("source", "start", "macro_name")

    def __str__(self):
        # because pylint doesn't understand that instance 'text' is str, not CharField
        # pylint: disable=unsubscriptable-object
        return '{}:{} - {}'.format(self.line, self.start, self.text[:100])

    def to_dict(self):
        """Write record attributes to a dictionary, for easy conversion to JSON."""
        the_pkg = self.source.pkg
        my_fields = {"id": self.pk,
                     "file": self.source.file_path,
                     "start": self.start,
                     "line": self.line,
                     "text": self.text,
                     "name": self.macro_name}
        return the_pkg.add_keys_to_dict(my_fields)


# Actually redundant info, as TownnewsSiteMetaData can reference packages that are not
# (currently) in the database
class CertifiedUsedBy(models.Model):
    """Implements many-to-many relationship between certified packages and sites.

    Could possibly use ManyToManyField, but I think it will need custom code.

    """
    package = models.ForeignKey(Package, models.CASCADE, null=False, blank=False)
    site = models.ForeignKey(TownnewsSite, models.CASCADE, null=False, blank=False)

    class Meta:  # pylint: disable=C0111
        unique_together = ("package", "site")

    # override
    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        if "package" not in exclude:
            if not self.package.is_certified:
                raise ValidationError("Non-certified package is only related to one site")
