from django.shortcuts import render
from django.http import HttpResponse
from .models import NewsPaper, TNSite


def index(request):
    context = {"papers": NewsPaper.objects.all()}
    return render(request, 'papers/index.html', context=context)

