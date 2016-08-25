# -*- coding:utf-8 -*-
"""Views of models in :py:mod:`utl_files`."""
import urllib

from django.shortcuts import render, get_object_or_404
from django import get_version
from django.http.response import Http404
from jsonview.decorators import json_view

from papers.models import TownnewsSite
from .models import Package, UTLFile, MacroRef, MacroDefinition, Application, CertifiedUsedBy

# pylint: disable=no-member


def home(request):
    """Display the main page: user selects site, skins, and that sets context for searches."""
    pkgs = Package.objects.all()
    active_sites = set()
    for pkg in pkgs:
        if pkg.site:
            active_sites.add(pkg.site.domain)

    context = {"active_sites": active_sites,
               "djvers": get_version()}
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


def search(request, macro_name=None):
    """A page to do macro searches -- will probably become tab on home."""
    if macro_name is None:
        macro_defs = MacroDefinition.objects.all()
    else:
        macro_defs = MacroDefinition.objects.filter(name=macro_name)
    pkgs = Package.objects.all()
    active_sites = set([pkg.site.domain for pkg in pkgs if pkg.site is not None])
    active_sites = active_sites - {"certified"}

    context = {"macros": macro_defs, "macro_name": macro_name, "active_sites": active_sites,
               "djvers": get_version()}
    return render(request, 'utl_files/search.html', context)


@json_view
def api_macro_refs(_, macro_name):
    """API call to find references to a specific macro."""
    refs = MacroRef.objects.filter(macro_name=macro_name)
    refs = [ref.to_dict() for ref in refs]
    return refs


def interpret_boolean(some_string):
    if isinstance(some_string, bool):
        return some_string
    if some_string.lower() in {"yes", "true", "y"}:
        return True
    if some_string.lower() in {"no", "false", "n"}:
        return False
    raise Http404("Unrecoginzed boolean: '{}' -- use 'true' or 'false'".format(some_string))

@json_view
def api_macro_defs_search(_, macro_name, search_certified=True, search_custom=True,
                          search_site=None):
    """Search for macro definitions based on name, and optionally whether the macro's package is
    certified or customized, and by site.

    """
    search_certified = interpret_boolean(search_certified)
    search_custom = interpret_boolean(search_custom)

    mdefs = MacroDefinition.objects.filter(name=macro_name)
    if not mdefs.exists():
        # we check this again below, but this avoids unnecessary work
        raise Http404("No macro named '{}' was found.".format(macro_name))
    if not search_certified and not search_custom:
        raise Http404("Search must check custom packages, certified packages, or both.")

    pkgs = Package.objects.all()
    if not search_certified:
        pkgs = pkgs.filter(is_certified=False)
    elif not search_custom:
        pkgs = pkgs.filter(is_certified=True)

    if search_custom and search_site:
        the_site = get_object_or_404(TownnewsSite, domain=search_site)
        pkgs = pkgs.filter(site=the_site)

    files = UTLFile.objects.filter(pkg__in=pkgs)
    mdefs.filter(source__in=files)
    return [mdef.to_dict() for mdef in mdefs]


@json_view
def api_macro_defs(_, macro_name, pkg_name=None, pkg_version=None, file_path=None):
    """API call to find the definition(s) of a macro."""
    utl_files = None
    pkgs = []

    mdefs = MacroDefinition.objects.filter(name=macro_name)
    if not mdefs.exists():
        # we check this again below, but this avoids unnecessary work
        raise Http404("No macro named '{}' was found.".format(macro_name))

    # build lists for filters based on other criteria
    if pkg_name is not None:
        if pkg_version is not None:
            pkgs = list(Package.objects.filter(name=pkg_name, version=pkg_version))
        else:
            pkgs = list(Package.objects.filter(name=pkg_name))

    # if file_path is not None and '/' in file_path:
        # file_path = quote_plus(file_path)

    if file_path is not None:
        file_path = file_path.replace('%2F', '/').replace('%2f', '/')
        utl_files = []
        for pkg in pkgs:
            ufiles = UTLFile.objects.filter(pkg=pkg, file_path=file_path)
            utl_files += list(ufiles)
    elif pkgs:
        utl_files = list(UTLFile.objects.filter(pkg__in=pkgs))

    if utl_files is not None:
        mdefs = mdefs.filter(source__in=utl_files)

    if not mdefs.exists():
        raise Http404("No macro named '{}' was found.".format(macro_name))

    return [mdef.to_dict() for mdef in mdefs]


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
    return [pkg.to_dict() for pkg in pkgs]


@json_view
def api_macro_text(_, macro_id):
    """Return the text of a macro definition, identified by integer ID `macro_id`."""
    macro = get_object_or_404(MacroDefinition, pk=macro_id)
    return {"text": macro.text, "line": macro.line, "name": macro.name,
            "source": macro.source.file_path, "package": macro.source.pkg.name, }


@json_view
def api_macro_w_syntax(_, macro_id):
    """Return the text of a macro with ID `macro_id`, with highlighting markup."""
    macro = get_object_or_404(MacroDefinition, pk=macro_id)
    return {"text": macro.text_with_markup, "line": macro.line, "name": macro.name,
            "source": macro.source.file_path, "package": macro.source.pkg.name, }


@json_view
def api_global_skins_for_site(_, site_url):
    """Returns the package names of all global skins associated with the
    :py:class:`TownnewsSite` record whose URL == `site_url`.

    """
    # "certified" will return 0 skins -- but don't trigger Site Not Found error
    # as it's supposed to act like a site
    if site_url == "certified":
        return []
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
        skins = Package.objects.filter(is_certified=True, pkg_type=Package.SKIN)
    else:
        site = get_object_or_404(TownnewsSite, URL='http://' + site_url)
        skins = Package.objects.filter(site=site, pkg_type=Package.SKIN)
    skin_list = []
    for skin in skins:
        if skin.app and skin.app.name != 'global':
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
        app, _ = pkg_name.split("::")
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

    # we have the global and app skin. Now add all blocks and components.
    for pkg in Package.objects.filter(site=the_site,
                                      pkg_type__in=[Package.BLOCK, Package.COMPONENT]):
        matched_pkgs.append(pkg)
    if site_domain != "certified":
        for certif in CertifiedUsedBy.objects.filter(site=the_site):
            if certif.package.pkg_type in [Package.BLOCK, Package.COMPONENT]:
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
            the_pkg = get_object_or_404(Package, is_certified=True, name=pkg_name, app=app,
                                        version=pkg_version)
        else:
            the_pkg = get_object_or_404(Package, is_certified=True, name=pkg_name,
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


def get_packages_for_site_with_skins(site_domain, global_pkg_name, skin_app, skin_name):
    """Return an iterable of all the packages known to be applicable to a
    given site, using a specific global skin.

    """
    pass


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


# api/macrorefs_for_site_with_skins/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)/
@json_view
def api_macrorefs_for_site_with_skins(_, macro_name, site_domain, global_pkg_name,
                                      skin_app, skin_name):
    """Return a list of all the references to a given macro from the set of
    packages likely to be active for a site, with a particular global skin
    active, and a particular skin applied.

    :param str macro_name: The name of the macro called.

    :param str site_domain: The site's domain (i.e. URL of front page with 'http://' removed)

    :param str global_pkg_name: The name of the global skin active for the site.

    :param str skin_app: The application containing the skin.

    :param str skin_name: The name of the skin in BLOX.

    """
    pass


# api/file_text_w_syntax/([^/]+)/
@json_view
def api_file_text_w_syntax(_, file_id):
    utl_file = get_object_or_404(UTLFile, pk=file_id)
    isinstance(utl_file, UTLFile)
    return {'pkg': utl_file.pkg.id,
            'file_path': utl_file.file_path,
            'text': utl_file.text_with_markup}


def certified_file_w_syntax(request, package_name, package_version, file_name):
    the_pkg = get_object_or_404(Package, name=package_name, is_certified=True,
                                version=package_version)
    the_path = urllib.parse.unquote(file_name)
    utl_file = get_object_or_404(UTLFile, pkg=the_pkg, file_path=the_path)
    markup_text = utl_file.text_with_markup.replace('\n', '<br>')
    # markup_text = markup_text.replace('[%', '<span class="utl_delim">[%</span>')
    context = {"file_name": the_path,
               "file_text": utl_file.file_text,
               "markup": markup_text}
    return render(request, "utl_files/file_display.html", context)
