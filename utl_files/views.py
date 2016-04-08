# -*- coding:utf-8 -*-
"""Views of models in :py:mod:`utl_files`."""
from urllib.parse import quote_plus

from django.shortcuts import render, HttpResponse, get_object_or_404
from jsonview.decorators import json_view

from .models import Package, UTLFile, MacroRef, MacroDefinition, Application
from papers.models import TownnewsSite

# pylint: disable=no-member


def home(request):
    """Display the main page: user selects site, skins, and that sets context for searches."""
    pkgs = Package.objects.all()
    active_sites = set(["certified"])
    for pkg in pkgs:
        if pkg.site:
            active_sites.add(pkg.site.domain)

    context = {"active_sites": active_sites}
    return render(request, 'utl_files/index.html', context)


def demo(request):  # pragma: no cover
    """Display a hand-crafted demo page for figuring out what generated output should be."""
    context = {"sites": TownnewsSite.objects.all(),
               "pkgs": Package.objects.all(),
               "apps": Application.objects.all(), }
    return render(request, 'utl_files/demo.html', context)


def search(request, macro_name):
    """A page to do macro searches -- will probably become tab on home."""
    macros = MacroDefinition.objects.filter(name=macro_name)
    context = {"macros": macros, "macro_name": macro_name}
    return render(request, 'utl_files/search.html', context)


@json_view
def api_macro_refs(_, macro_name):
    """API call to find references to a specific macro."""
    refs = MacroRef.objects.filter(macro_name=macro_name)
    return list(refs) if refs else []


@json_view
def api_macro_defs(_, macro_name, pkg_name=None, pkg_version=None, file_path=None):
    """API call to find the definition(s) of a macro."""
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

    return [mdef.to_dict() for mdef in defs]


@json_view
def api_applications(_):
    """API call to return list of known applications."""
    return [app.name for app in Application.objects.all()]


@json_view
def api_packages(_, name=None, version=None):
    """Return JSON list package names (if name is :py:attr:`None`), list available versions (if
    version is :py:attr:`None`), or list all info about a particular package (if both provided).

    """
    if name is None:
        pkgs = Package.objects.all()
    elif version is None:
        pkgs = Package.objects.filter(name=name)
    else:
        pkgs = [get_object_or_404(Package, name=name, version=version)]
    return [{"name": pkg.name, "version": pkg.version} for pkg in pkgs]


def api_macro_text(_, macro_id):
    """Return the text of a macro definition, identified by integer ID `macro_id`."""
    macro = get_object_or_404(MacroDefinition, pk=macro_id)
    return HttpResponse(content=macro.text)


@json_view
def api_global_skins_for_site(_, site_url):
    """Returns the package names of all global skins associated with the
    :py:class:`TownnewsSite` record whose URL == `site_url`.

    """
    site = get_object_or_404(TownnewsSite, URL='http://' + site_url)
    skins = Package.objects.filter(site=site, pkg_type=Package.GLOBAL_SKIN)
    return [skin.name for skin in skins]


@json_view
def api_app_skins_for_site(_, site_url):
    """Returns the package names of all application skins associated with the
    :py:class:`TownnewsSite` record whose URL == `site_url`.

    """
    site = get_object_or_404(TownnewsSite, URL='http://' + site_url)
    skins = Package.objects.filter(site=site, pkg_type=Package.SKIN)
    skin_list = []
    for skin in skins:
        if skin.app:
            skin_list.append("{}::{}".format(skin.app.name, skin.name))
        else:
            skin_list.append(skin.name)
    return skin_list


@json_view
def api_files_for_custom_pkg(_, site_url, pkg_name, pkg_last_download):
    """Returns a list of files in the customized package.

    :param str site_url: The site's main URL, omitting the 'http://' prefix

    :param str pkg_name: The name of the package in BLOX ('true' name, not displayed name)

    :param str pkg_last_download: The date/time of the package's last download

    :returns: Returns a list of files (as path names relative to the package)

    """
    site = get_object_or_404(TownnewsSite, URL='http://' + site_url)
    pkg = Package.objects.get(site=site, name=pkg_name, last_download=pkg_last_download)
    return [f.file_path for f in UTLFile.objects.filter(pkg=pkg)]
