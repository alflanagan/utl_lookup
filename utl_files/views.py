# -*- coding:utf-8 -*-

import json

from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Package, UTLFile, MacroRef, MacroDefinition, UTLFilesJsonEncoder, Application


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


def api_macro_defs(request, macro_name):
    defs = MacroDefinition.objects.filter(name=macro_name)
    if defs:
        response = HttpResponse(content=json.dumps(list(defs), cls=UTLFilesJsonEncoder))
    else:
        response = HttpResponse(content='{}')
    return response


def api_applications(request):
    apps = Application.objects.all()
    return HttpResponse(content=json.dumps(list(apps), cls=UTLFilesJsonEncoder))

def api_packages(request, name=None, version=None):
    """Return JSON list package names (if name is None), list available versions (if version is None),
    or list all info about a particular package (if both provided).

    """
    if name is None:
        pkgs = Package.objects.all()
        version_list = []
        for pkg in pkgs:
            version_list.append({"name": pkg.name, "version": pkg.version})
        return HttpResponse(content=json.dumps(version_list))
    elif version is None:
        pkgs = Package.objects.all(name=name)
        version_list = []
        for pkg in pkgs:
            version_list.append({"name": pkg.name, "version": pkg.version})
        return HttpResponse(content=json.dumps(version_list))
    else:
        pkg = get_object_or_404(Package, name=name, version=version)
        return HttpResponse(content=json.dumps(pkg.to_dict()))
