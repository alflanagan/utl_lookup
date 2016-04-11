"Models for objects related to a particular newspaper."
from django.db import models

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


class NewsPaper(models.Model):
    """The newspaper organization associated with a site."""
    name = models.CharField(max_length=100,
                            unique=True,
                            help_text="The official name of the newspaper.")

    def __str__(self):
        return self.name
