"Models for objects related to a particular newspaper."
from pathlib import Path
import json
from datetime import datetime

from django.db import models
from django.utils import timezone
from pytz import common_timezones
# pylint: disable=no-member


class TownnewsSite(models.Model):
    """A Townnews website, referred to by its main URL and managed as a unit."""
    URL = models.URLField(max_length=250, unique=True, help_text="The sites main URL")
    name = models.CharField(max_length=100,
                            blank=True,
                            help_text="The site brand (may be same as URL)")
    """Some sites refer to their site by the domain. Others brand it with the paper's name. Still
    others have a separate name they use.

    """
    paper = models.ForeignKey('NewsPaper',
                              help_text="The paper that owns this site.",
                              on_delete=models.CASCADE)

    def __str__(self):
        return self.name if self.name else self.URL

    @property
    def domain(self):
        """The URL without the 'http://' prefix, occasionally useful. (The dummy site for
        certified packages will return 'certified')

        """
        # special case
        if self.URL == "http://townnews.com":
            return "certified"
        return self.URL.replace('http://', '')


class TownnewsSiteMetaData(models.Model):
    """Additional information about the site, such as what packages are
    associated with it (even if they're not in database) and their last
    download times).

    """
    class Meta:  # pylint:disable=C0111,R0903
        # not sure last_download should be in here.
        unique_together = ['site', 'pkg_name', 'version', 'last_download']

    site = models.ForeignKey('TownnewsSite',
                             help_text='The site this metadata applies to',
                             on_delete=models.CASCADE)
    # we flatten the structure of site_meta.json a bit so we don't deal
    # w/nested data. If a Package record exists for the package, this data
    # should be there as well.
    # fields should be compatible with Package definitions!
    pkg_name = models.CharField(max_length=250, help_text="TownNews name for this package.")
    zip_name = models.FilePathField(max_length=2000)
    version = models.CharField(max_length=20,
                               help_text="Version number for the package as a whole.")
    is_certified = models.BooleanField(help_text="Is officially certified/supported by TownNews.")
    last_download = models.DateTimeField(help_text="When this package's ZIP file was downloaded.")

    @staticmethod
    def _date_from_str(floatstr):
        """Utility method to convert float-style string in JSON file to a date."""
        naive_date = datetime.fromtimestamp(float(floatstr))
        return timezone.make_aware(naive_date)

    @classmethod
    def load_file(cls, file_name, site):
        """Loads site data from a JSON site_meta.json file."""
        file_name = Path(file_name) if not isinstance(file_name, Path) else file_name
        with file_name.open('r') as metain:
            data = json.load(metain, parse_float=cls._date_from_str)
        for key in data:
            rcd = data[key]
            new_md = cls(site=site, pkg_name=key, version=rcd["version"],
                         zip_name=rcd["zip_name"], last_download=rcd["last_download"],
                         is_certified=True if rcd["certified"] == 'Y'else False)
            new_md.full_clean()
            new_md.save()


class NewsPaper(models.Model):
    """The newspaper organization associated with a site."""
    name = models.CharField(max_length=100,
                            unique=True,
                            help_text="The official name of the newspaper.")

    def __str__(self):
        return self.name
