"""Classes to model UTL files in a Townnews site, including file organization."""
import os
from django.db import models

from papers.models import TNSite

# pylint: disable=W0232,R0903,E1101


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
    site = models.ForeignKey(TNSite)
    app = models.ForeignKey(Application)

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ["name", "version", "site", "app"]  # Too many key fields

    def __str__(self):
        return "{}/{}/{} [{}]".format(self.app, self.name, self.version, self.site)

    def load_from(self, directory):
        """Loads a Townnews package from a directory (and subdirectories)."""
        self.save()
        props = {}
        with open(os.path.join(directory, 'package/config.ini'), 'r') as propin:
            for line in propin:
                key, value = line[:-1].split('=')
                props[key] = value[1:-1]
        for key in props:
            new_prop = PackageProps(self, key, props[key])
            new_prop.save()

        deps = {}
        with open(os.path.join(directory, 'package/dependencies.ini'), 'r') as depin:
            for line in depin:
                key, value = line[:-1].split('=')
                deps[key] = value.replace('"', '')
        for key in deps:
            new_dep = PackageDep(self, key, deps[key])
            dep_pkg = Package.objects.query(name=key, version=deps[key])
            if dep_pkg:
                new_dep.dep_pkg = dep_pkg
            new_dep.save()


class PackageProps(models.Model):
    """Properties for a package. Any key-value pair except those that have their own field in
    :py:class:`utl_files.models.Package`.

    """
    pkg = models.ForeignKey(Package)
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ("pkg", "key")
        verbose_name = "Package Properties"


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
        verbose_name = "Package Dependency"

    def __str__(self):
        return "{} ({})".format(self.dep_name, self.dep_version)

    def check_for_deps(self):
        """Looks for dependencies which don't have pointer to Package table. For each, checks
        whether dependency exists and if found, adds it to the dep_pkg field.

        """
        for dep in PackageDep.objects.query(dep_pkg=None):
            # only look for certified packages for now. Handling of custom packages need to be
            # redone (FIXME).
            dep_pkg = Package.objects.query(name=self.dep_name, version=self.dep_version,
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
