"""Classes to model UTL files in a Townnews site, including file organization."""
import os
from django.db import models

from papers.models import TNSite
# pylint: disable=W0232,R0903,E1101


class PackageError(Exception):
    "Catchall for exceptions raised by Package class"


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
    name = models.CharField(max_length=250)
    version = models.CharField(max_length=20)
    is_certified = models.BooleanField()
    app = models.ForeignKey(Application)

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ["name", "version"]

    def __str__(self):
        return "{}/{}/{}".format(self.app, self.name, self.version)

    @classmethod
    def load_from(cls, directory):
        """Loads a Townnews package from a directory (and subdirectories)."""
        props = {}
        with open(os.path.join(directory, 'package/config.ini'), 'r') as propin:
            for line in propin:
                key, value = line[:-1].split('=')
                props[key] = value[1:-1]

        application = Application.objects.filter(name=props["app"])
        if not application:
            application = Application(name=props["app"])
            application.save()
        else:
            application = application[0]
        certified = os.path.exists(os.path.join(directory, '.certification'))
        if Package.objects.filter(name=props["name"], version=props["version"]).exists():
            raise PackageError("Package '{}', version '{}' is already loaded.\n To load again,"
                               " first remove the existing package from the data."
                               "".format(props["name"], props["version"]))
        new_pkg = cls(name=props["name"], version=props["version"], is_certified=certified,
                      app=application)
        new_pkg.save()
        for key in props:
            if key not in ["name", "version", "app"]:
                new_prop = PackageProp(pkg=new_pkg, key=key, value=props[key])
                new_prop.save()

        deps = {}
        with open(os.path.join(directory, 'package/dependencies.ini'), 'r') as depin:
            for line in depin:
                key, value = line[:-1].split('=')
                deps[key] = value.replace('"', '')
        for key in deps:
            new_dep = PackageDep(pkg=new_pkg, dep_name=key, dep_version=deps[key])
            dep_pkg = Package.objects.filter(name=key, version=deps[key])
            if dep_pkg:
                new_dep.dep_pkg = dep_pkg
            new_dep.save()


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
    pkg = models.ForeignKey(Package)
    dep_name = models.CharField(max_length=200)  # name; always present
    dep_pkg = models.ForeignKey(Package, null=True,
                                related_name="dep_pkg")  # may be Null if package not in db.
    dep_version = models.CharField(max_length=50, blank=False)

    class Meta:  # pylint: disable=missing-docstring
        # one version of a package is dependent on at most one version of another package
        unique_together = ("pkg", "dep_name")
        verbose_name = "package dependency"
        verbose_name_plural = "package dependencies"

    def __str__(self):
        return "{} ({})".format(self.dep_name, self.dep_version)

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
    file = models.FileField(upload_to='utl_files')
    file_path = models.FilePathField(allow_folders=False)
    pkg = models.ForeignKey(Package)

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ("pkg", "file_path")
        verbose_name = "UTL File"

    def __str__(self):
        return "{}/{}:{}".format(self.pkg.app, self.pkg.name, self.file_path)
