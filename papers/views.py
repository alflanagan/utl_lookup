from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. This is the index page of the app, where you'll"
                        " choose a web site to work with, and have various search options.")

