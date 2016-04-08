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
from io import TextIOWrapper, StringIO

from django.test import TestCase
from django.core.handlers.wsgi import WSGIRequest
from wsgiref.util import FileWrapper

from utl_files import views
from utl_files.models import Application, Package, UTLFile
from papers.models import NewsPaper, TownnewsSite


def make_wsgi_request(request_text):
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
               'HTTP_USER_AGENT': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
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
        {"name": "editorial-core-mobile",
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
        """Unit tests for :py:func:`~utl_files.views.ap_files_for_custom_pkg`."""
        request = None

        for record in self.TEST_PACKAGES:
            response = views.api_files_for_custom_pkg(request, record["site"].replace('http://', ''),
                                                      record["name"], record["last_download"])
        json_out = response.getvalue().decode('utf-8')
        file_list = json.loads(json_out)
        self.assertSetEqual(set(self.TEST_FILES), set(file_list))


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
        request = make_wsgi_request('/files')
        response = views.home(request)
        result = response.content.decode('utf-8')
        for fragment in self.EXPECTED_RESULT:
            self.assertIn(fragment, result)
        active_sites = set()
        for pkg in Package.objects.all():
            active_sites.add(pkg.site.domain)
        for tnsite in TownnewsSite.objects.all():
            if tnsite.domain in active_sites:
                self.assertIn('<li value="{0}">{0}</li>'.format(tnsite.domain),
                              result)
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


# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
