#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_files.views`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods,no-member,invalid-name
import sys
from copy import deepcopy
import json
from io import StringIO
from wsgiref.util import FileWrapper
from datetime import datetime

import pytz
from django.test import TestCase
from django.http import HttpRequest
from django.core.handlers.wsgi import WSGIRequest

from utl_files import views
from utl_files.models import Application, Package, UTLFile
from papers.models import NewsPaper, TownnewsSite


def make_wsgi_request(request_text):
    """Create a :py:class:`WSGIRequest` instance for the query GET ``request_text``."""
    the_input = StringIO()
    environ = {'wsgi.file_wrapper': FileWrapper,
               'SERVER_SOFTWARE': 'WSGIServer/0.2',
               'KDEDIRS': '/usr',
               'WINDOWID': '54525973',
               'GATEWAY_INTERFACE': 'CGI/1.1',
               'REQUEST_METHOD': 'GET',
               'LANG': 'en_US.UTF-8',
               'SERVER_PORT': '8002',
               'wsgi.input': the_input,
               'TZ': 'America/New_York',
               'wsgi.run_once': 'False',
               'SSH_CONNECTION': '10.200.232.27 49483 172.16.250.74 22',
               'XDG_SESSION_ID': '7508',
               'SSH_CLIENT': '10.200.232.27 49483 22',
               'REMOTE_HOST': '',
               'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.5',
               'DJANGO_SITENAME': 'utl_lookup',
               'DJANGO_SETTINGS_MODULE': 'utl_lookup.settings',
               'REMOTE_ADDR': '127.0.0.1',
               'RUN_MAIN': 'true',
               'wsgi.url_scheme': 'http',
               'HTTP_USER_AGENT': ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) '
                                   'Gecko/20100101 Firefox/45.0'),
               'CONTENT_LENGTH': '',
               'SERVER_PROTOCOL': 'HTTP/1.1',
               'PYTHONIOENCODING': 'UTF-8',
               'HTTP_DNT': '1',
               'HTTP_COOKIE': 'csrftoken=QGvB7Xnpr0P17ZBUf1eBFUIb3iSSAXVv',
               'wsgi.version': '(1, 0)',
               'QUERY_STRING': '',
               'wsgi.multithread': 'True',
               'PWD': '/mnt/extra/Devel/utl_lookup',
               'CONTENT_TYPE': 'text/plain',
               'wsgi.multiprocess': 'False',
               'HTTP_ACCEPT_ENCODING': 'gzip, deflate',
               'wsgi.errors': sys.stderr,
               'SERVER_NAME': 'localhost.localdomain',
               'HTTP_HOST': 'localhost:8002',
               'HTTP_CONNECTION': 'keep-alive',
               'USER': 'aflanagan',
               'SCRIPT_NAME': '',
               'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', }
    the_input.write(request_text)
    my_request = WSGIRequest(environ)
    return my_request


class api_global_skins_for_siteTestCase(TestCase):
    """Unit tests for function :py:func:`~utl_files.views.api_global_skins_for_site`."""

    @classmethod
    def setUpTestData(cls):
        try:
            cls.paper = NewsPaper.objects.get(name='The Richmond Times-Dispatch')
        except NewsPaper.DoesNotExist:
            cls.paper = NewsPaper(name='The Richmond Times-Dispatch')
            cls.paper.save()

        try:
            cls.tn_site = TownnewsSite(name='RTD')
        except TownnewsSite.DoesNotExist:
            cls.tn_site = TownnewsSite(URL='http://richmond.com', name='RTD', paper=cls.paper)
            cls.tn_site.save()

    def test_create(self):
        """Unit test for :py:meth:`utl_files.views.api_global_skins_for_site`."""
        response = views.api_global_skins_for_site(None, "richmond.com")
        self.assertEqual(response.getvalue(), b'[]')


class api_files_for_custom_pkgTestCase(TestCase):
    """Unit tests for function :py:func:`~utl_files.views.api_files_for_custom_pkg`."""

    TEST_PAPERS = [{"name": "agNET Ag News & Commodities"}]

    TEST_PACKAGES = [
        {"name": "editorial::editorial-core-mobile",
         "version": "1.54.0.0",
         "is_certified": True,
         "app": "editorial",
         "last_download": "2016-02-27T13:12:11Z",
         "disk_directory": "certified/skins/editorial/editorial-core-mobile_1.54.0.0",
         "site": "http://agnet.net",
         "pkg_type": "s", }
    ]

    # TODO: Fix UTLFile.
    TEST_FILES = [
        "templates/front.html.utl",
        "templates/index.html.utl",
        "templates/401.html.utl",
        "templates/content.audio.html.utl",
        "includes/_ads/mobile-bottom.inc.utl",
        "includes/_ads/mobile-story.inc.utl",
        "includes/_ads/mobile-top.inc.utl",
        "includes/_mobile/_site/mobile.sections.inc.utl",
        "includes/_mobile/mobile.footer.inc.utl",
        "includes/_mobile/mobile.header.inc.utl",
        "includes/_mobile/mobile.login.inc.utl",
        "includes/_mobile/mobile.service-notice.inc.utl",
        "includes/tabs.main.inc.utl",
        "includes/tabs.sidebar.inc.utl",
        "includes/tabs.sidebar_bottom.inc.utl",
        "includes/tabs.sidebar_middle.inc.utl",
        "templates/403.html.utl",
        "templates/404.html.utl",
        "templates/content.article.html.utl",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.papers = []
        for record in cls.TEST_PAPERS:
            try:
                new_ppr = NewsPaper.objects.get(name=record["name"])
            except NewsPaper.DoesNotExist:
                new_ppr = NewsPaper(**record)
                new_ppr.save()
            cls.papers.append(new_ppr)

        cls.pkgs = []
        for record in cls.TEST_PACKAGES:
            kwargs = deepcopy(record)
            # replace foreign key strings with object referenced
            kwargs["app"] = Application.objects.get(name=kwargs["app"])
            kwargs["site"] = TownnewsSite.objects.get(URL=kwargs["site"])
            # now I can just do this
            new_pkg = Package(**kwargs)
            new_pkg.save()
            cls.pkgs.append(new_pkg)

        for path in cls.TEST_FILES:
            new_file = UTLFile(file_path=path, pkg=cls.pkgs[0])
            new_file.full_clean()
            new_file.save()

    def test_success(self):
        """Unit tests for :func:`~utl_files.views.api_package_files_custom`."""
        request = HttpRequest()
        for record in self.TEST_PACKAGES:
            site_name = record["site"].replace('http://', '')
            self.assertTrue(TownnewsSite.objects.filter(URL=record["site"]).exists())
            site_obj = TownnewsSite.objects.get(URL=record["site"])
            self.assertTrue(Package.objects.filter())
            response = views.api_package_files_custom(
                request,
                record["site"].replace('http://', ''),
                record["name"])
        json_out = response.getvalue().decode('utf-8')
        file_list = json.loads(json_out)
        self.assertNotIn('error', file_list)
        path_list = [finfo["path"] for finfo in file_list]
        self.assertSetEqual(set(self.TEST_FILES), set(path_list))


class homeTestCase(TestCase):
    """Unit tests for :py:func:`utl_files.views.home`."""
    TEST_PAPERS = [{"name": "agNET Ag News & Commodities"}]

    TEST_PACKAGES = [
        {"name": "editorial-core-mobile",
         "version": "1.54.0.0",
         "is_certified": True,
         "app": "editorial",
         "last_download": "2016-02-27T13:12:11Z",
         "disk_directory": "certified/skins/editorial/editorial-core-mobile_1.54.0.0",
         "site": "http://agnet.net",
         "pkg_type": "s", }
    ]

    EXPECTED_RESULT = ['<!DOCTYPE html>',
                       '<meta charset="utf-8">',
                       '<title></title>',
                       '<div class="container">',
                       '<div class="row">',
                       'Townnews Template Cross-Reference',
                       '<div id="search-bar">',
                       'id="package-context-form"',
                       '<div id="id_site_div"',
                       '<button id="id_site_label"',
                       '<ul id="id_site"',
                       'id="selected_site"',
                       '<div id="id_global_skin_div"',
                       '<button id="id_global_skin_label"',
                       '<ul id="id_global_skin"',
                       '<div id="id_app_skin_div"',
                       '<button id="id_app_skin_label"',
                       '<ul id="id_app_skin"',
                       '<div id="tree-panel"',
                       '<li class="list-group-item"',
                       'id="pkgs_global_list"',
                       'id="pkgs_skin_list"',
                       'id="pkgs_blocks_list"',
                       'id="pkgs_components_list"',
                       '<div id="tab-panel"',
                       '<li id="files-tab"',
                       '<li id="defs-tab"',
                       '<li id="refs-tab"',
                       '<div id="files-panel"',
                       'id="files-tree"',
                       'id="files-tree-root"',
                       '<div id="defs-panel"',
                       '<div id="refs-panel"']
    """List of significant parts of generated page (significant mostly in the
    sense that other code expects them to be present).

    """

    @classmethod
    def setUpTestData(cls):
        cls.papers = []
        for record in cls.TEST_PAPERS:
            try:
                new_ppr = NewsPaper.objects.get(name=record["name"])
            except NewsPaper.DoesNotExist:
                new_ppr = NewsPaper(**record)
                new_ppr.save()
            cls.papers.append(new_ppr)

        cls.pkgs = []
        for record in cls.TEST_PACKAGES:
            kwargs = deepcopy(record)
            # replace foreign key strings with object referenced
            kwargs["app"] = Application.objects.get(name=kwargs["app"])
            kwargs["site"] = TownnewsSite.objects.get(URL=kwargs["site"])
            # now I can just do this
            new_pkg = Package(**kwargs)
            new_pkg.save()
            cls.pkgs.append(new_pkg)
        # Use our custom error messages in place of, rather than in addition
        # to, the standard error message
        cls.longMessage = False

    def test_view(self):
        """Basic rendering of page."""
        # verify "active" sites are shown in drop-down, not others
        request = make_wsgi_request('/files')
        response = views.home(request)
        result = response.content.decode('utf-8')
        for fragment in self.EXPECTED_RESULT:
            self.assertIn(fragment, result,
                          "'{}' not found in output page for /files.".format(fragment))
        active_sites = set()
        for pkg in Package.objects.all():
            active_sites.add(pkg.site.domain)
        for tnsite in TownnewsSite.objects.all():
            if tnsite.domain in active_sites:
                expected_tag = '<li value="{0}">{0}</li>'.format(tnsite.domain)
                self.assertIn(expected_tag, result,
                              "Missing expected '{}' in /files page.".format(expected_tag))
            else:
                self.assertNotIn(tnsite.domain, result)


class searchTestCase(TestCase):
    """Unit tests for :py:func:`utl_files.views.home`."""
    TEST_PAPERS = [{"name": "agNET Ag News & Commodities"}]

    TEST_PACKAGES = [
        {"name": "editorial-core-mobile",
         "version": "1.54.0.0",
         "is_certified": True,
         "app": "editorial",
         "last_download": "2016-02-27T13:12:11Z",
         "disk_directory": "certified/skins/editorial/editorial-core-mobile_1.54.0.0",
         "site": "http://agnet.net",
         "pkg_type": "s", }
    ]

    EXPECTED_RESULT = ['<!DOCTYPE html>',
                       '<meta charset="utf-8">',
                       '<meta http-equiv="X-UA-Compatible" content="IE=edge">',
                       '<meta name="viewport" content="width=device-width, initial-scale=1">',
                       '<div class="container">',
                       '<div class="row">',
                       '<h3 class="app-header text-center">Townnews Template Cross-Reference</h3>',
                       '<div id="search-bar">',
                       '<form class="form-inline" id="package-context-form" role="search">',
                       '<div id="id_site_div"',
                       '<button id="id_site_label"',
                       '<ul id="id_site" class="dropdown-menu"',
                       '<input type="hidden" id="selected_site">',
                       '<div id="id_global_skin_div"',
                       '<button id="id_global_skin_label"',
                       '<ul id="id_global_skin"',
                       '<div id="id_app_skin_div"',
                       '<button id="id_app_skin_label"',
                       '<ul id="id_app_skin"',
                       '<div id="tree-panel"',
                       '<h3 class="panel-title">',
                       '<ul class="list-group">',
                       '<li class="list-group-item">',
                       '<div id="tab-panel"',
                       '<div class="panel-body">', ]

    @classmethod
    def setUpTestData(cls):
        cls.papers = []
        for record in cls.TEST_PAPERS:
            try:
                new_ppr = NewsPaper.objects.get(name=record["name"])
            except NewsPaper.DoesNotExist:
                new_ppr = NewsPaper(**record)
                new_ppr.save()
            cls.papers.append(new_ppr)

        cls.pkgs = []
        for record in cls.TEST_PACKAGES:
            kwargs = deepcopy(record)
            # replace foreign key strings with object referenced
            kwargs["app"] = Application.objects.get(name=kwargs["app"])
            kwargs["site"] = TownnewsSite.objects.get(URL=kwargs["site"])
            # now I can just do this
            new_pkg = Package(**kwargs)
            new_pkg.save()
            cls.pkgs.append(new_pkg)

    def test_view(self):
        """Basic rendering of page."""
        # verify "active" sites are shown in drop-down, not others
        request = make_wsgi_request('/search')
        response = views.search(request, 'some-macro-name')
        result = response.content.decode('utf-8')
        # TODO: will probably get better results if we actually load some macros


class api_packages_for_site_with_skinsTestCase(TestCase):
    """Unit tests for function :py:func:`~utl_files.views.api_packages_for_site_with_skins`."""
    GSKIN_NAME = "global-richmond-portal_temp"
    ASKIN_NAME = "awesome-custom-skin"
    ASKIN_VER = "1.3.4"

    @classmethod
    def setUpTestData(cls):
        cls.app, _ = Application.objects.get_or_create(name="editorial")
        cls.gl_app, _ = Application.objects.get_or_create(name="global")
        cls.paper, _ = NewsPaper.objects.get_or_create(name='Richmond Times-Dispatch')
        cls.tn_site, _ = TownnewsSite.objects.get_or_create(URL='http://richmond.com',
                                                            name='RTD',
                                                            paper=cls.paper)
        cls.global_skin, _ = Package.objects.get_or_create(
            name=cls.GSKIN_NAME,
            version="",
            is_certified=False,
            app=cls.gl_app,
            last_download=datetime(1923, 3, 12, 10, 23, 0, tzinfo=pytz.utc),  # yapf: disable
            disk_directory="/my/stuff/richmond.com/global_skins/{}".format(cls.GSKIN_NAME),
            site=cls.tn_site,
            pkg_type=Package.GLOBAL_SKIN)
        cls.app_skin, _ = Package.objects.get_or_create(
            name=cls.ASKIN_NAME,
            version=cls.ASKIN_VER,
            is_certified=False,
            app=cls.app,
            last_download=datetime(1950, 1, 23, 16, 12, 38, tzinfo=pytz.utc),  # yapf: disable
            disk_directory="/my/stuff/richmond.com/skins/editorial/awesome-custom-skin_1.3.4/",
            site=cls.tn_site,
            pkg_type=Package.SKIN)

    def test_create(self):
        """Unit test for :py:meth:`utl_files.views.api_packages_for_site_with_skins`."""
        request = make_wsgi_request("files/api_packages_for_site_with_skins/{}/{}/N/{}/{}/{}/"
                                    "".format(self.tn_site.domain, self.GSKIN_NAME, self.app.name,
                                              self.ASKIN_NAME, self.ASKIN_VER))
        response = views.api_packages_for_site_with_skins(request, self.tn_site.domain,
                                                          self.GSKIN_NAME, self.app.name,
                                                          self.ASKIN_NAME)
        actual = json.loads(response.getvalue().decode('utf-8'))

        expected_all = {"global-richmond-portal_temp":
                        {"is_certified": "n",
                         "version": "",
                         "downloaded": "1923-03-12T10:23:00Z",
                         "name": "global-richmond-portal_temp",
                         "app": "global",
                         "location":
                         "/my/stuff/richmond.com/global_skins/global-richmond-portal_temp",
                         "pkg_type": "g", },
                        "awesome-custom-skin":
                        {"is_certified": "n",
                         "version": "1.3.4",
                         "downloaded": "1950-01-23T16:12:38Z",
                         "name": "awesome-custom-skin",
                         "app": "editorial",
                         "location":
                         "/my/stuff/richmond.com/skins/editorial/awesome-custom-skin_1.3.4/",
                         "pkg_type": "s", }}
        self.assertEqual(len(actual), len(expected_all))
        self.assertNotIn("error", actual)
        for pkg_dict in actual:
            expected = expected_all[pkg_dict["name"]]
            self.assertDictContainsSubset(expected, pkg_dict)

        # Local Variables:
        # python-indent-offset: 4
        # fill-column: 100
        # indent-tabs-mode: nil
        # End:
