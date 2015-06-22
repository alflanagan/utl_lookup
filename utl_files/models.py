"""Classes to model UTL files in a Townnews site, including file organization."""
from django.db import models

# pylint: disable=W0232,R0903


class Application(models.Model):
    """A Townnews application, or group of related functionality."""
    name = models.CharField(max_length=50, unique=True)


class TNSite(models.Model):
    """A Townnews website, referred to by its main URL and managed as a unit."""
    URL = models.URLField(max_length=250, unique=True)
    name = models.CharField(max_length=100)


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


class UTLFile(models.Model):
    """Reference information regarding a specific file in the UTL templates directories."""
    file = models.FileField(upload_to='utl_files')
    file_path = models.FilePathField(allow_folders=False)
    pkg = models.ForeignKey(Package)

    class Meta:  # pylint: disable=missing-docstring
        unique_together = ["pkg", "file_path"]
