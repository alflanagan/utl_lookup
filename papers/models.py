"Models for objects related to a particular newspaper."
from django.db import models


class TownnewsSite(models.Model):
    """A Townnews website, referred to by its main URL and managed as a unit."""
    URL = models.URLField(max_length=250, unique=True,
                          help_text="The sites main URL")
    name = models.CharField(max_length=100, blank=True,
                            help_text="The site brand (may be same as URL)")
    """Some sites refer to their site by the domain. Others brand it with the paper's name. Still
    others have a separate name they use.

    """
    paper = models.ForeignKey('NewsPaper', help_text="The paper that owns this site.",
                              on_delete=models.CASCADE)

    def __str__(self):
        return self.name if self.name else self.URL


class NewsPaper(models.Model):
    """The newspaper organization associated with a site."""
    name = models.CharField(max_length=100,
                            unique=True, help_text="The official name of the newspaper.")

    def __str__(self):
        return self.name
