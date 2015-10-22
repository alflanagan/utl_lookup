"Models for objects related to a particular newspaper."
from django.db import models


class TNSite(models.Model):
    """A Townnews website, referred to by its main URL and managed as a unit."""
    URL = models.URLField(max_length=250, unique=True)
    name = models.CharField(max_length=100, blank=True)
    paper = models.ForeignKey('NewsPaper', help_text="The paper that owns this site.",
                              on_delete=models.CASCADE)

    class Meta:  # pylint: disable=C0111,R0903
        verbose_name = "Townnews Site"

    def __str__(self):
        return self.name if self.name else self.URL


class NewsPaper(models.Model):
    """The newspaper organization associated with a site."""
    name = models.CharField(max_length=100,
                            unique=True, help_text="The official name of the newspaper.")

    def __str__(self):
        return self.name

