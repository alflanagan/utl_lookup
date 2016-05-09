# -*- coding:utf-8 -*-
"""Views of models in :py:mod:`utl_files`."""
from urllib.parse import quote_plus

from django.shortcuts import render, get_object_or_404
from django.http.response import Http404
from jsonview.decorators import json_view

from .models import Package, UTLFile, MacroRef, MacroDefinition, Application, CertifiedUsedBy
from papers.models import TownnewsSite

# pylint: disable=no-member


def home(request):
    """Display the main page: user selects site, skins, and that sets context for searches."""
    pkgs = Package.objects.all()
    active_sites = set()
    for pkg in pkgs:
        if pkg.site:
            active_sites.add(pkg.site.domain)

    context = {"active_sites": active_sites}
    return render(request, 'utl_files/index.html', context)


def macros(request):
    """Display a macro cross-reference page. Similar to home, but macro-oriented."""
    pkgs = Package.objects.all()
    active_sites = set()
    for pkg in pkgs:
        if pkg.site and pkg.site.domain != "certified":
            active_sites.add(pkg.site.domain)

    context = {"active_sites": active_sites}
    return render(request, 'utl_files/macros.html', context)


def demo(request):  # pragma: no cover
    """Display a hand-crafted demo page for figuring out what generated output should be."""
    context = {"sites": TownnewsSite.objects.all(),
               "pkgs": Package.objects.all(),
               "apps": Application.objects.all(), }
    return render(request, 'utl_files/demo.html', context)


def search(request, macro_name):
    """A page to do macro searches -- will probably become tab on home."""
    macro_defs = MacroDefinition.objects.filter(name=macro_name)
    context = {"macros": macro_defs, "macro_name": macro_name}
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


@json_view
def api_macro_text(_, macro_id):
    """Return the text of a macro definition, identified by integer ID `macro_id`."""
    macro = get_object_or_404(MacroDefinition, pk=macro_id)
    return {"text": macro.text, "line": macro.line, "name": macro.name,
            "source": macro.source.file_path, "package": macro.source.pkg.name,}


@json_view
def api_global_skins_for_site(_, site_url):
    """Returns the package names of all global skins associated with the
    :py:class:`TownnewsSite` record whose URL == `site_url`.

    """
    # "certified" will return 0 skins -- but don't trigger Site Not Found error
    if site_url == "certified":
        site = get_object_or_404(TownnewsSite, URL="http://townnews.com")
    else:
        site = get_object_or_404(TownnewsSite, URL='http://' + site_url)
    skins = Package.objects.filter(site=site, pkg_type=Package.GLOBAL_SKIN)
    return [skin.name for skin in skins]


@json_view
def api_app_skins_for_site(_, site_url):
    """Returns the package names of all application skins associated with the
    :py:class:`TownnewsSite` record whose URL == `site_url`.

    """
    if site_url == "certified":
        site = get_object_or_404(TownnewsSite, URL='http://townnews.com')
    else:
        site = get_object_or_404(TownnewsSite, URL='http://' + site_url)
    skins = Package.objects.filter(site=site, pkg_type=Package.SKIN)
    skin_list = []
    for skin in skins:
        if skin.app:
            skin_list.append("{}::{}".format(skin.app.name, skin.name))
        else:
            skin_list.append(skin.name)
    return skin_list

# RTD/core_site_richmond(2016-03-03 18:32)
# api/package_files/richmond.com/core_site_richmond/
# api/package_files/omaha.com/editorial%3A%3Aeditorial-custom-widget/
@json_view
def api_package_files_custom(_, site_url, pkg_name):
    """Returns a list of files in the customized package.

    :param str site_url: The site's main URL, omitting the 'http://' prefix

    :param str pkg_name: The name of the package in BLOX. If the package is a skin, the name
        should have the format application name + "::" + package name. (In a URL, "::" is
        "%3A%3A")

    :returns: Returns a list of dictionaries of :py:class:`~utl_files.models.UTLFile` values
        (from :py:meth:`~utl_files.models.UTLFile.to_dict`)

    """
    site = get_object_or_404(TownnewsSite, URL='http://' + site_url)
    if "::" in pkg_name:
        app, pkg_name = pkg_name.split("::")
        app = get_object_or_404(Application, name=app)
    else:
        app = get_object_or_404(Application, name="global")

    pkg = get_object_or_404(Package, site=site, name=pkg_name, app=app)
    return [f.to_dict() for f in UTLFile.objects.filter(pkg=pkg)]


# /files/api/api_packages_for_site_with_skins/richmond.com/global-richmond-portal_temp/
# editorial/custom-newsletter-bordered/

# pylint: disable=invalid-name
@json_view
def api_packages_for_site_with_skins(_, site_domain, global_pkg_name, skin_app, skin_name):
    """Return a list of all the packages which apply to a page on a particular site, with a
    particular global skin active, and a particular skin applied.

    :param str site_domain: The site's domain (i.e. URL of front page with 'http://' removed) OR
        "certified" to get certified packages.

    :param str global_pkg_name: The name of the global skin active for the site. Ignored if
        `site_domain` is "certified".

    :param str skin_app: The application containing the skin.

    :param str skin_name: The name of the skin in BLOX.

    """
    # "certified" is a special case
    if site_domain != 'certified':
        the_site = get_object_or_404(TownnewsSite, URL='http://{}'.format(site_domain))
        global_app = get_object_or_404(Application, name='global')
        pkg_app = get_object_or_404(Application, name=skin_app)

        global_skins = Package.objects.filter(site=the_site, app=global_app, name=global_pkg_name)
        if not global_skins.exists():
            raise Http404("No global skin '{}' found for site '{}'".format(global_pkg_name,
                                                                           the_site.URL))
        # just get most recent download
        global_skin = global_skins.latest('last_download')

        # Is there a customized app skin?
        custom_app_skin = Package.objects.filter(site=the_site, app=pkg_app, name=skin_name)
        selected_skin = None
        if custom_app_skin.exists():
            selected_skin = custom_app_skin.latest('last_download')
        else:
            # try to find certified package to match
            # TODO: improve this by checking CertifiedUsedBy first
            cert_pkgs = Package.objects.filter(is_certified=True, app=pkg_app, name=skin_name)
            if cert_pkgs.exists():
                for cert_pkg in cert_pkgs:
                    used_by = CertifiedUsedBy.objects.filter(package=cert_pkg, site=the_site)
                    if used_by.exists():
                        selected_skin = cert_pkg
                        break
                if selected_skin is None:
                    # we don't have an entry in CertifiedUsedBy. How did we get here?
                    # never mind, try to find matching certified package
                    selected_skin = cert_pkgs.latest('last_download')
            else:
                raise Http404("Unable to find app skin {}::{}".format(skin_app, skin_name))

        matched_pkgs = [global_skin, selected_skin]
    else:
        # certified has no skins
        matched_pkgs = []
        # special "dummy" site
        the_site = get_object_or_404(TownnewsSite, URL='http://townnews.com')

    for pkg in Package.objects.filter(site=the_site,
                                      pkg_type__in=[Package.BLOCK, Package.COMPONENT]):
        matched_pkgs.append(pkg)
    if site_domain != "certified":
        for certif in CertifiedUsedBy.objects.filter(site=the_site):
            matched_pkgs.append(certif.package)

    return [pkg.to_dict() for pkg in matched_pkgs]


@json_view
def api_package_files_certified(_, pkg_name, pkg_version=None):
    """Return a list of all the files in a certified package.

    :param str pkg_name: The name of the package in BLOX. If the package is a skin, the name
        should have the format application name + "::" + package name. (In a URL, "::" is
        "%3A%3A")

    :param str version: The package version. If ommitted, and only one record is found, returns
        that, otherwise returns 404 error.

    """
    app = None
    if "::" in pkg_name:
        app, pkg_name = pkg_name.split("::")
        app = get_object_or_404(Application, name=app)

    if pkg_version:
        if app:
            the_pkg = get_object_or_404(Package, is_certified=True, name=pkg_name,
                                        version=pkg_version)
        else:
            the_pkg = get_object_or_404(Package, is_certified=True, name=pkg_name, app=app,
                                        version=pkg_version)
    else:
        try:
            if app:
                the_pkg = get_object_or_404(Package, is_certified=True, name=pkg_name, app=app)
            else:
                the_pkg = get_object_or_404(Package, is_certified=True, name=pkg_name)
        except Package.MultipleObjectsReturned:
            raise Http404("Can't determine files for certified package '{}' without version"
                          "".format(pkg_name))

    utlfiles = UTLFile.objects.filter(pkg=the_pkg)

    results = []
    for utlfile in utlfiles:
        results.append(utlfile.to_dict())
    return results
# pylint: disable=invalid-name


# api/macros_for_site_with_skins/([^/]+)/([^/]+)/([^/]+)/([^/]+)/
@json_view
def api_macros_for_site_with_skins(_, site_domain, global_pkg_name, skin_app, skin_name):
    """Return a list of all the macros likely to be active for a site, with a particular global
    skin active, and a particular skin applied.

    :param str site_domain: The site's domain (i.e. URL of front page with 'http://' removed)

    :param str global_pkg_name: The name of the global skin active for the site.

    :param str skin_app: The application containing the skin.

    :param str skin_name: The name of the skin in BLOX.

    """
    the_site = get_object_or_404(TownnewsSite, URL='http://{}'.format(site_domain))
    global_app = get_object_or_404(Application, name='global')
    pkg_app = get_object_or_404(Application, name=skin_app)

    global_skins = Package.objects.filter(site=the_site, app=global_app, name=global_pkg_name)
    if not global_skins.exists():
        raise Http404("No global skin '{}' found for site '{}'".format(global_pkg_name,
                                                                       the_site.URL))
    # just get most recent download
    global_skin = global_skins.latest('last_download')

    # Is there a customized app skin?
    custom_app_skin = Package.objects.filter(site=the_site, app=pkg_app, name=skin_name)
    selected_skin = None
    if custom_app_skin.exists():
        selected_skin = custom_app_skin.latest('last_download')
    else:
        # try to find certified package to match
        cert_pkg = get_object_or_404(CertifiedUsedBy, site=the_site, package__app=pkg_app,
                                     package_name=skin_name)
        selected_skin = cert_pkg.package

    matched_pkgs = set([global_skin, selected_skin])

    for pkg in Package.objects.filter(site=the_site,
                                      pkg_type__in=[Package.BLOCK, Package.COMPONENT]):
        matched_pkgs.add(pkg)

    for certif in CertifiedUsedBy.objects.filter(site=the_site,
                                                 package__pkg_type__in=[Package.BLOCK,
                                                                        Package.COMPONENT]):
        matched_pkgs.add(certif.package)

    utl_files = UTLFile.objects.filter(pkg__in=matched_pkgs)
    macro_defs = MacroDefinition.objects.filter(source__in=utl_files)
    results = [macro_def.to_dict() for macro_def in macro_defs]
    results.sort(key=lambda x: x["name"])
    return results
