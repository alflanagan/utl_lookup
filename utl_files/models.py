"""Classes to model UTL files in a Townnews site, including file organization."""
from django.db import models

from papers.models import TNSite

# pylint: disable=W0232,R0903


class Application(models.Model):
    """A Townnews application, or group of related functionality."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
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
