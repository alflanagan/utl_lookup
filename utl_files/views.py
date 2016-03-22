# -*- coding:utf-8 -*-
"""Views of models in :py:mod:`utl_files`."""
import json
from urllib.parse import quote_plus

from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Package, UTLFile, MacroRef, MacroDefinition, UTLFilesJsonEncoder, Application
from .forms import XrefContextForm
from papers.models import TownnewsSite


# pylint: disable=no-member

def home(request):
    pkgs = Package.objects.all()
    context = {"packages": pkgs,
               "the_form": XrefContextForm()}
    return render(request, 'utl_files/index.html', context)


def search(request, macro_name):
    macros = MacroDefinition.objects.filter(name=macro_name)
    context = {"macros": macros,
               "macro_name": macro_name}
    return render(request, 'utl_files/search.html', context)


def api_macro_refs(_, macro_name):
    refs = MacroRef.objects.filter(macro_name=macro_name)
    if refs:
        response = HttpResponse(content=json.dumps(list(refs), cls=UTLFilesJsonEncoder))
    else:
        response = HttpResponse(content='{}')
    return response


def api_macro_defs(_, macro_name, pkg_name=None, pkg_version=None, file_path=None):
    utl_file = None
    source_pkg = None
    if file_path is not None and '/' in file_path:
        file_path = quote_plus(file_path)
    if pkg_name is not None and pkg_version is not None:
        source_pkg = get_object_or_404(Package, name=pkg_name, version=pkg_version)
    if source_pkg is not None and file_path is not None:
        utl_file = get_object_or_404(UTLFile, file_path=file_path)
    if utl_file is not None:
        defs = MacroDefinition.objects.filter(name=macro_name, source=utl_file)
    elif source_pkg is not None:
        utl_files = UTLFile.objects.filter(pkg=source_pkg)
        defs = []
        for utl_file in utl_files:
            some_defs = MacroDefinition.objects.filter(name=macro_name, source=utl_file)
            defs += some_defs
    else:
        # take advantage of fact you can't name a macro with just a number
        try:
            defs = MacroDefinition.objects.filter(pk=int(macro_name))
        except ValueError:
            defs = MacroDefinition.objects.filter(name=macro_name)

    if defs:
        response = HttpResponse(content=json.dumps(list(defs), cls=UTLFilesJsonEncoder))
    else:
        response = HttpResponse(content='{}')
    return response


def api_applications(_):
    apps = Application.objects.all()
    return HttpResponse(content=json.dumps(list(apps), cls=UTLFilesJsonEncoder))


def api_packages(_, name=None, version=None):
    """Return JSON list package names (if name is :py:attr:`None`), list available versions (if
    version is :py:attr:`None`), or list all info about a particular package (if both provided).

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


def api_macro_text(_, macro_id):
    """Return the text of a macro definition, identified by integer ID `macro_id`."""
    macro = get_object_or_404(MacroDefinition, pk=macro_id)
    return HttpResponse(content=macro.text)


def api_global_skins_for_site(_, site_name):
    """Returns the package names of all global skins associated with the :py:class:`TownnewsSite`
    record whose name == `site_name`.

    """
    site = get_object_or_404(TownnewsSite, name=site_name)
    skins = Package.objects.query(site=site, pkg_type=Package.GLOBAL_SKIN)
    skin_names = [skin.name for skin in skins]
    return HttpResponse(content=json.dumps(skin_names))
