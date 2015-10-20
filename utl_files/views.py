# -*- coding:utf-8 -*-

import json

from django.shortcuts import render, HttpResponse
from .models import Package, UTLFile, MacroRef, MacroDefinition, UTLFilesJsonEncoder


def home(request):
    pkgs = Package.objects.all()
    context = {"packages": pkgs}
    return render(request, 'utl_files/index.html', context)


def search(request, macro_name):
    macros = MacroDefinition.objects.filter(name=macro_name)
    context = {"macros": macros}
    return render(request, 'utl_files/search.html', context)

def api_macro_refs(request, macro_name):
    refs = MacroRef.objects.filter(macro_name=macro_name)
    if refs:
        response = HttpResponse(content=json.dumps(list(refs), cls=UTLFilesJsonEncoder))
    else:
        response = HttpResponse(content='{}')
    return response
