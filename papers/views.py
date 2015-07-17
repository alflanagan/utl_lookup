from django.shortcuts import render

from .models import NewsPaper, TNSite


def index(request):
    """Main page for the site, quick access to search functionality."""
    context = {"papers": NewsPaper.objects.all()}  # pylint: disable=E1101
    return render(request, 'papers/index.html', context=context)
