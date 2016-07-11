#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_files.views`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods,no-member,invalid-name,too-many-lines

#    yes, the module's too long, but we're following the Django standard and
#    keeping everything in one file (why?)
import sys
from copy import deepcopy
import json
from io import StringIO
from wsgiref.util import FileWrapper
from datetime import datetime
from pathlib import Path
from warnings import simplefilter

import pytz
from django.test import TestCase
from django.http import HttpRequest, HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.conf import settings

from utl_files import views
from utl_files.models import (Application, Package, UTLFile, MacroDefinition,
                              MacroRef, CertifiedUsedBy)
from utl_files.more_tests import TestCaseMixin
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


class homeTestCase(TestCase, TestCaseMixin):
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


class macrosTestCase(TestCase):
    "Unit tests for view :py:func:`utl_files.views.macros`."

    EXPECTED = [b'<button id="id_site_label" type="button" data-toggle="dropdown"',
                b'<ul id="id_site"',
                b'<li value="agnet.net">agnet.net',
                b'<button id="id_global_skin_label" type="button" data-toggle="dropdown"',
                b'<ul id="id_global_skin"',
                b'<button id="id_app_skin_label" type="button" data-toggle="dropdown"',
                b'<ul id="id_app_skin"',
                b'<div id="tree-panel"',
                b'<div id="tree-view"',
                b'<ul class="list-group" id="macros-list">',
                b'<div id="tab-panel"',
                b'<div id="macro-name"',
                b'<div id="macro-package-name"',
                b'<div id="macro-file-name"',
                b'<li id="defs-tab"',
                b'<li id="refs-tab"',
                b'<div id="defs-panel"',
                b'<div id="defs-text"',
                b'<div id="refs-panel"', ]

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

    @classmethod
    def setUpTestData(cls):
        cls.request = make_wsgi_request('/files/macros')
        cls.papers = []
        for ppr in cls.TEST_PAPERS:
            new_ppr = NewsPaper.objects.get_or_create(name=ppr['name'])
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
        """Unit test for :py:func:`utl_files.views.macros`."""
        response = views.macros(self.request)
        self.assertEqual(response.status_code, 200)
        for substring in self.EXPECTED:
            self.assertIn(substring, response.content)


class MacroTestCase(TestCaseMixin, TestCase):
    """Parent class for macro-related API call test cases that need similar
    data setup.

    """

    TEST_DIR = Path('utl_files/test_data/api_macro_text')
    TEST_DATA = ['macrodefs.json', 'packages.json', 'utlfiles.json']

    app_keys = {51: "global", 47: "editorial"}

    @classmethod
    def _load_test_pkgs(cls):
        """Read fields for test packages from external file."""
        with (cls.TEST_DIR / 'packages.json').open("r") as pkgin:
            pkg_data = json.load(pkgin)
        for pkg in pkg_data:
            datum = pkg["fields"]
            the_site = None
            if datum['site'] is not None:
                # slimy hack around having to rely on site PK being the same in the future
                the_site = TownnewsSite.objects.get(URL='http://kearneyhub.com')
            the_app = Application.objects.get(name=cls.app_keys[datum['app']])
            new_pkg = Package(site=the_site,
                              app=the_app,
                              name=datum['name'],
                              version=datum['version'],
                              last_download=datum['last_download'],
                              is_certified=datum['is_certified'],
                              disk_directory=datum['disk_directory'],
                              pkg_type=datum['pkg_type'])
            new_pkg.full_clean()
            new_pkg.save()

    @classmethod
    def _load_test_files(cls):
        """Load test UTLFile data from an external file."""
        cls.test_files = []
        with (cls.TEST_DIR / 'utlfiles.json').open('r') as ufilein:
            ufile_text = ufilein.read()
            ufile_data = json.loads(ufile_text)
        for uf in ufile_data:
            uf_datum = uf["fields"]
            the_pkg = Package.objects.get(name=uf_datum["pkg"])
            new_uf = UTLFile(pkg=the_pkg, file_path=uf_datum["file_path"],
                             file_text=uf_datum["file_text"])
            new_uf.full_clean()
            new_uf.save()
            cls.test_files.append(new_uf)

    @classmethod
    def _load_macro_defs(cls):
        """Load test macro definitions from external file."""
        with (cls.TEST_DIR / 'macrodefs.json').open('r') as mdefin:
            mdef_data = json.load(mdefin)
        cls.test_ids = []
        for mdef in mdef_data:
            mdef_datum = mdef["fields"]
            parts = mdef_datum["source"].split('/')
            the_pkg = Package.objects.get(name=parts[0])
            fpath = "/".join(parts[1:])
            the_file = UTLFile.objects.get(pkg=the_pkg,
                                           file_path=fpath)
            new_mdef = MacroDefinition(source=the_file,
                                       text=mdef_datum["text"],
                                       name=mdef_datum["name"],
                                       start=mdef_datum["start"],
                                       end=mdef_datum["end"],
                                       line=mdef_datum["line"])
            new_mdef.full_clean()
            new_mdef.save()
            cls.test_ids.append(new_mdef.pk)

    @classmethod
    def setUpTestData(cls):
        """Load macro definitions to retrieve."""
        cls.the_site = TownnewsSite.objects.get(URL='http://kearneyhub.com')
        cls.the_app = Application.objects.get(name="global")

        cls._load_test_pkgs()

        cls._load_test_files()

        cls._load_macro_defs()


class searchTestCase(MacroTestCase):
    """Unit tests for view :py:func:`utl_files.views.search`."""

    EXPECTED = {
        'photo_text': [
            b'<div id="pkg-file-list"',
            b'<button type="button"',
            b'core-asset-index-lead_presentation [1.23.1]',
            b'block.utl',
            b'<button type="button"',
            b'core-asset-index-map [1.21.1]',
            b'block.utl',
            b'<div id="macro-defn"',
            b'<div id="macro-code-display"',
            b'<div id="macro-ref-display"', ],
        'time_updated': [
            b'<div id="pkg-file-list"',
            b'<button type="button"',
            b'core-asset-index-map [1.21.1]',
            b'block.utl',
            b'<div id="macro-defn"',
            b'<div id="macro-code-display"',
            b'<div id="macro-ref-display"', ],
        'build_slideshow_presentation_nav_items': [
            b'<div id="pkg-file-list"',
            b'<button type="button"',
            b'core-slideshow-presentation-1-15-1-test_block [0.1]',
            b'block.utl',
            b'<div id="macro-defn"',
            b'<div id="macro-code-display"',
            b'<div id="macro-ref-display"', ], }

    def test_basic(self):
        """Simple unit test for :py:func:`utl_files.views.search`."""
        self.assertGreater(MacroDefinition.objects.count(), 3)
        for macro in MacroDefinition.objects.all():
            request = make_wsgi_request('/files/macro/{}'.format(macro.name))
            response = views.search(request, macro.name)
            self.assertEqual(response.status_code, 200)
            for substring in self.EXPECTED[macro.name]:
                self.assertIn(substring, response.content)


class api_macro_refsTestCase(MacroTestCase):
    """Unit tests for :py:func:`utl_files.views.api_macro_refs`."""

    REFERENCES = [{
        'start': 1230,
        'line': 53,
        'text': 'fred = photo_text(asset.photo)',
        'macro_name': 'photo_text', }]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        utl_file = cls.test_files[0]
        cls.macro_refs = []
        for record in cls.REFERENCES:
            new_ref = MacroRef(source=utl_file,
                               start=record['start'],
                               line=record['line'],
                               text=record['text'],
                               macro_name=record['macro_name'])
            new_ref.full_clean()
            new_ref.save()
            cls.macro_refs.append(new_ref)

    def test_basic(self):
        """Simple unit test for :py:func:`utl_files.views.api_macro_refs`."""
        request = make_wsgi_request('/files/api/macro_refs/photo_text')
        response = views.api_macro_refs(request, 'photo_text')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 1)
        expected = {'line': 53,
                    'pkg_name': 'core-asset-index-lead_presentation',
                    'pkg_version': '1.23.1',
                    'name': 'photo_text',
                    'file': 'includes/block.utl',
                    'text': 'fred = photo_text(asset.photo)',
                    'start': 1230,
                    'pkg_certified': False,
                    'pkg_download': '2016-03-09T22:41:50Z',
                    'pkg_site': 'http://kearneyhub.com', }
        self.assertDictContainsSubset(data[0], expected)

        self.assertSetEqual(set(['id']), set(data[0].keys()) - set(expected.keys()))
        # verify we can use data to retrieve related records
        the_site = TownnewsSite.objects.get(URL=expected['pkg_site'])
        matching_pkgs = Package.objects.filter(name=expected['pkg_name'],
                                               version=expected['pkg_version'],
                                               is_certified=expected['pkg_certified'],
                                               site=the_site,
                                               last_download=expected['pkg_download'])
        self.assertEqual(matching_pkgs.count(), 1)


class api_macro_defsTestCase(MacroTestCase):
    """Unit tests for :py:func:`utl_files.views.api_macro_defs`."""

    def test_one_arg(self):
        """Unit test for call to :py:func:`utl_files.views.api_macro_defs`
        with a single argument.

        """
        request = make_wsgi_request('/files/api/macro_defs/photo_text/')
        response = views.api_macro_defs(request, 'photo_text')
        results = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), 2)
        expected_results = {7951: {'end': 8359,
                                   'file': 'includes/block.utl',
                                   'line': 177,
                                   'name': 'photo_text',
                                   'pkg_certified': False,
                                   'pkg_download': '2016-03-09T22:41:50Z',
                                   'pkg_name': 'core-asset-index-lead_presentation',
                                   'pkg_site': 'http://kearneyhub.com',
                                   'pkg_version': '1.23.1',
                                   'start': 7951},
                            7359: {'end': 7694,
                                   'file': 'block.utl',
                                   'line': 206,
                                   'name': 'photo_text',
                                   'pkg_certified': False,
                                   'pkg_download': '2016-03-09T22:41:50Z',
                                   'pkg_name': 'core-asset-index-map',
                                   'pkg_site': 'http://kearneyhub.com',
                                   'pkg_version': '1.21.1',
                                   'start': 7359}}

        for record in results:
            expected = expected_results[record['start']]
            self.assertDictContainsSubset(record, expected)
            self.assertSetEqual(set(['id']),
                                set(record.keys()) - set(expected.keys()))

    def test_two_args(self):
        """Unit test for call to :py:func:`utl_files.views.api_macro_defs` with two arguments."""
        request = make_wsgi_request('/files/api/macro_defs/photo_text/'
                                    'core-asset-index-lead_presentation/')
        response = views.api_macro_defs(request, 'photo_text', 'core-asset-index-lead_presentation')
        results = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), 1)
        expected = {'end': 8359,
                    'file': 'includes/block.utl',
                    'line': 177,
                    'name': 'photo_text',
                    'pkg_certified': False,
                    'pkg_download': '2016-03-09T22:41:50Z',
                    'pkg_name': 'core-asset-index-lead_presentation',
                    'pkg_site': 'http://kearneyhub.com',
                    'pkg_version': '1.23.1',
                    'start': 7951}

        self.assertDictContainsSubset(results[0], expected)
        self.assertSetEqual(set(['id']),
                            set(results[0].keys()) - set(expected.keys()))

    def test_multi_args(self):
        """Unit test for call to :py:func:`utl_files.views.api_macro_defs` with all arguments."""
        params = ['photo_text', 'core-asset-index-lead_presentation', '1.23.1',
                  'includes%2Fblock.utl']
        url = '/files/api/macro_defs/{}/'.format("/".join(params))
        request = make_wsgi_request(url)
        response = views.api_macro_defs(request, *params)
        results = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), 1)
        expected = {'end': 8359,
                    'file': 'includes/block.utl',
                    'line': 177,
                    'name': 'photo_text',
                    'pkg_certified': False,
                    'pkg_download': '2016-03-09T22:41:50Z',
                    'pkg_name': 'core-asset-index-lead_presentation',
                    'pkg_site': 'http://kearneyhub.com',
                    'pkg_version': '1.23.1',
                    'start': 7951}

        self.assertDictContainsSubset(results[0], expected)
        self.assertSetEqual(set(['id']),
                            set(results[0].keys()) - set(expected.keys()))

    def test_no_macro_found(self):
        """Unit tests for call to :py:func:`utl_files.views.api_macro_defs`
        with macro criteria that don't find anything.

        """
        request1 = make_wsgi_request('/files/api/macro_defs/no_such_macro')
        response1 = views.api_macro_defs(request1, 'no_such_macro')
        results1 = json.loads(response1.content.decode('utf-8'))
        self.assertEqual(response1.status_code, 404)
        self.assertIn('error', results1)

        params = ['photo_text', 'core-asset-index-lead_presentation', '1.23.1', 'no_such_file.utl']
        url = '/files/api/macro_defs/{}/'.format("/".join(params))
        request2 = make_wsgi_request(url)
        response2 = views.api_macro_defs(request2, *params)
        results2 = json.loads(response2.content.decode('utf-8'))
        self.assertEqual(response2.status_code, 404)
        self.assertIn('error', results2)


class api_applicationsTestCase(TestCase):
    """Unit test for :py:func:`utl_files.views.api_applications`."""

    def test_call(self):
        """Call takes no params, so test single case."""
        request = make_wsgi_request('/files/api/applications')
        response = views.api_applications(request)
        self.assertEqual(response.status_code, 200)
        apps = json.loads(response.content.decode('utf-8'))
        expected = []
        for app_record in Application.objects.all():
            expected.append(app_record.name)
        self.assertSetEqual(set(apps), set(expected))


class api_packagesTestCase(MacroTestCase):
    """Unit tests for :py:func:`utl_files.views.api_packages`."""

    expected = [{'app': 'global',
                 'downloaded': '2016-03-09T22:41:50Z',
                 'is_certified': 'n',
                 'location': 'agnet.net/blocks/core-asset-index-lead_presentation_1.23.1',
                 'name': 'core-asset-index-lead_presentation',
                 'pkg_type': 'b',
                 'site': 'http://kearneyhub.com',
                 'version': '1.23.1'},
                {'app': 'global',
                 'downloaded': '2016-03-09T22:41:50Z',
                 'is_certified': 'n',
                 'location': 'agnet.net/blocks/core-asset-index-map_1.21.1',
                 'name': 'core-asset-index-map',
                 'pkg_type': 'b',
                 'site': 'http://kearneyhub.com',
                 'version': '1.21.1'},
                {'app': 'global',
                 'downloaded': '2016-03-09T22:43:01Z',
                 'is_certified': 'n',
                 'location': 'agnet.net/blocks/core-slideshow-presentation-1-15-1-test_block_0.1',
                 'name': 'core-slideshow-presentation-1-15-1-test_block',
                 'pkg_type': 'b',
                 'site': 'http://kearneyhub.com',
                 'version': '0.1'},
                {"version": "1.41.0.1",
                 "app": 'global',
                 "name": "core-alert-breaking_news_fader",
                 "pkg_type": "b",
                 "site": None,
                 "location": "certified/blocks/core-alert-breaking_news_fader_1.41.0.1",
                 "downloaded": "2016-03-22T17:57:48Z",
                 "is_certified": "y", },
                {"version": "1.0",
                 "app": "editorial",
                 "name": "kh-base",
                 "pkg_type": "s",
                 "site": "http://kearneyhub.com",
                 "location": "kearneyhub.com/skins/editorial/kh-base_1.0",
                 "downloaded": "2016-06-08T20:15:49Z",
                 "is_certified": "n", },
                {"version": "1.30.1",
                 "app": "editorial",
                 "name": "editorial-core-base",
                 "pkg_type": "s",
                 "site": None,
                 "location": "certified/skins/editorial/editorial-core-base_1.30.1",
                 "downloaded": "2015-02-20T21:55:40Z",
                 "is_certified": "y", }]

    def test_get_all(self):
        """Unit test for :py:func:`utl_files.views.api_packages` with no arguments."""
        request = make_wsgi_request('/files/api/packages/')
        response = views.api_packages(request)
        results = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), Package.objects.count())
        match_count = 0  # failsafe
        for data in self.expected:
            for result in results:
                if data['name'] == result['name']:
                    self.assertDictContainsSubset(result, data)
                    match_count += 1
        self.assertEqual(match_count, len(results),
                         "Failed to match a package by name.")

    def test_one_arg(self):
        """Unit test for :py:func:`utl_files.views.api_packages` with one argument."""
        pkg_name = "core-asset-index-lead_presentation"
        request = make_wsgi_request('/files/api/packages/{}/'.format(pkg_name))
        response = views.api_packages(request, pkg_name)
        results = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), 1)
        match_count = 0  # failsafe
        for data in self.expected:
            for result in results:
                if data['name'] == result['name']:
                    self.assertDictContainsSubset(result, data)
                    match_count += 1
        self.assertEqual(match_count, len(results),
                         "Failed to match a package by name.")

    def test_two_args(self):
        """Unit test for :py:func:`utl_files.views.api_packages` with two arguments."""
        pkg_name = 'core-asset-index-map'
        pkg_version = '1.21.1'
        request = make_wsgi_request('/files/api/packages/{}/{}/'.format(pkg_name, pkg_version))
        response = views.api_packages(request, pkg_name, pkg_version)
        results = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), 1)
        match_count = 0  # failsafe
        for data in self.expected:
            for result in results:
                if data['name'] == result['name']:
                    self.assertDictContainsSubset(result, data)
                    match_count += 1
        self.assertEqual(match_count, len(results),
                         "Failed to match a package by name.")


class api_macro_textTestCase(MacroTestCase):
    """Unit tests for :py:func:`~utl_files.views.api_macro_text`."""

    def test_basic_call(self):
        """Unit test of basic call to API."""
        for mdef_id in self.test_ids:
            mdef = MacroDefinition.objects.get(pk=mdef_id)
            request = make_wsgi_request("files/api/macro_text/{}/"
                                        "".format(mdef_id))

            results = views.api_macro_text(request, mdef_id)
            self.assertEqual(results.status_code, 200)
            actual = json.loads(results.content.decode('utf-8'))
            expected = {'package': mdef.source.pkg.name,
                        'line': mdef.line,
                        'source': mdef.source.file_path,
                        'name': mdef.name}
            self.assertDictContainsSubset(actual, expected)
            self.assertSetEqual(set(['text']),
                                set(actual.keys()) - set(expected.keys()))
            self.assertEqual(mdef.text, actual['text'])

    def test_no_such_macro(self):
        """Unit test of call to api_macro_text with a nonexistent macro name."""
        mdef_id = 1000
        self.assertFalse(MacroDefinition.objects.filter(pk=mdef_id).exists())
        request = make_wsgi_request("files/api/macro_text/{}/"
                                    "".format(mdef_id))
        results = views.api_macro_text(request, mdef_id)
        self.assertEqual(results.status_code, 404)
        actual = json.loads(results.content.decode('utf-8'))
        self.assertIn('error', actual)


class api_macro_w_syntaxTestCase(MacroTestCase):
    """Unit tests for :py:func:`~utl_files.`"""

    EXPECTED = [r'\[%\s*<span class="statement_list"><span class="macro_defn"><span class='
                r'"macro_decl">macro photo_text</span><!-- macro_decl --> %\]<span class="statement'
                r'_list"><span class="document">\s*</span><!-- document -->\[%\s*<span class="if">'
                r'if <span class="expr"><span class="expr"><span class="id">photo_credit</span><!--'
                r' id --> == <span class="literal">&#x27;true&#x27;</span><!-- literal --></span>'
                r'<!-- expr --> &amp;&amp; <span class="id">credit</span><!-- id --></span><!-- '
                r'expr --> %\]<span class="statement_list"><span class="document">&lt;div class='
                r'"photo-byline"&gt;</span><!-- document -->\s*\[%\s*<span class="id">photo_credit'
                r'_text</span><!-- id -->;\s*<span class="expr"><span class="id">credit</span><!--'
                r' id --> | <span class="id">html</span><!-- id --></span><!-- expr -->;\s*<span '
                r'class="id">credit</span><!-- id --> %\]\s*<span class="document">\s*&lt;/div&gt;'
                r'\s*</span><!-- document --></span><!-- statement_list -->\s*\[%\s*end</span><!-- '
                r'if -->;\s* <span class="comment">/\* photo_credit \*/\s*</span><!-- comment -->'
                r'\s*<span class="if">\s*if <span class="expr"><span class="expr"><span class="id">'
                r'photo_caption</span><!-- id --> == <span class="literal">&#x27;true&#x27;</span>'
                r'<!-- literal --></span><!-- expr --> &amp;&amp; <span class="id">caption</span>'
                r'<!-- id --></span><!-- expr --> %\]<span class="statement_list"><span class='
                r'"document">\s*&lt;div class=&quot;photo-cutline&quot;&gt;\s*</span><!-- document'
                r' -->\s*\[% <span class="expr"><span class="id">caption</span><!-- id --> | <span'
                r' class="id">html</span><!-- id --></span><!-- expr -->;\s*<span class="id">'
                r'caption</span><!-- id --> %\]<span class="document">\s*&lt;/div&gt;\s*</span><!--'
                r' document --></span><!-- statement_list -->\s*\[%\s*end</span><!-- if --></span>'
                r'<!-- statement_list -->; /* photo caption */\nend</span><!-- macro_defn --> %\]'
                r'</span><!-- statement_list -->', ]

    def test_basic_call(self):
        """Unit test of basic call to API."""
        for mdef_id in self.test_ids:
            mdef = MacroDefinition.objects.get(pk=mdef_id)
            request = make_wsgi_request("files/api/macro_text/{}/"
                                        "".format(mdef_id))

            results = views.api_macro_w_syntax(request, mdef_id)
            self.assertEqual(results.status_code, 200)
            from_json = json.loads(results.content.decode('utf-8'))
            self.assertDictContainsSubset(from_json,
                                          {'package': mdef.source.pkg.name,
                                           'line': mdef.line,
                                           'source': mdef.source.file_path,
                                           'name': mdef.name})
            if mdef.name == 'photo_text':
                self.assertRegex(from_json['text'], self.EXPECTED[0])


class api_global_skins_for_siteTestCase(MacroTestCase):
    """Unit tests for function :py:func:`~utl_files.views.api_global_skins_for_site`."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.site = TownnewsSite.objects.get(URL='http://kearneyhub.com')
        cls.app = Application.objects.get(name='global')
        new_global_skin = Package(site=cls.site,
                                  app=cls.the_app,
                                  last_download=datetime(2016, 6, 8, 20, 15, 49,
                                                         tzinfo=timezone.utc),
                                  is_certified=False,
                                  disk_directory=('kearneyhub.com/global_skins/'
                                                  'global-kh-oct-2013-dev'),
                                  name='global-kh-oct-2013-dev',
                                  version='0.1',
                                  pkg_type='g')
        new_global_skin.full_clean()
        new_global_skin.save()

    def test_call_success(self):
        """Unit test for :py:meth:`utl_files.views.api_global_skins_for_site`."""
        request = make_wsgi_request('/files/api/global_skins_for_site/kearneyhub.com')
        response = views.api_global_skins_for_site(request, "kearneyhub.com")
        self.assertEqual(response.status_code, 200)
        results = json.loads(response.content.decode('utf-8'))
        self.assertSequenceEqual(results, ['global-kh-oct-2013-dev'])

    def test_call_not_found(self):
        """Unit test for :py:meth:`utl_files.views.api_global_skins_for_site`
        where no skin is found.

        We return empty list for the case where a site exists but has no
        global skins, but raise a 404 error if the site does not exist.

        """
        request = make_wsgi_request('/files/api/global_skins_for_site/richmond.com')
        response = views.api_global_skins_for_site(request, "richmond.com")
        self.assertEqual(response.status_code, 200)
        results = json.loads(response.content.decode('utf-8'))
        self.assertSequenceEqual(results, [])

        # try it with pseudo-site "certified"
        request = make_wsgi_request('/files/api/global_skins_for_site/certified')
        response = views.api_global_skins_for_site(request, "certified")
        self.assertEqual(response.status_code, 200)
        results = json.loads(response.content.decode('utf-8'))
        self.assertSequenceEqual(results, [])

        # try it with a site that is just not there
        request = make_wsgi_request('/files/api/global_skins_for_site/foobar.com')
        response = views.api_global_skins_for_site(request, "foobar.com")
        self.assertEqual(response.status_code, 404)
        results = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', results)


class api_app_skins_for_siteTestCase(MacroTestCase):
    """Unit tests for :py:func:`utl_files.views.api_app_skins_for_site`."""
    def test_call(self):
        """Unit test for successful call of
        :py:func:`utl_files.views.api_app_skins_for_site`.

        """
        sitename = 'kearneyhub.com'
        request = make_wsgi_request('/files/api/app_skins_for_site/{}/'.format(sitename))
        response = views.api_app_skins_for_site(request, sitename)
        self.assertEqual(response.status_code, 200)
        results = json.loads(response.content.decode('utf-8'))
        self.assertSequenceEqual(results, ['editorial::kh-base'])

    def test_certified_call(self):
        """Unit test for call of
        :py:func:`utl_files.views.api_app_skins_for_site` for certified
        packages.

        """
        sitename = 'certified'
        request = make_wsgi_request('/files/api/app_skins_for_site/{}/'.format(sitename))
        response = views.api_app_skins_for_site(request, sitename)
        self.assertEqual(response.status_code, 200)
        results = json.loads(response.content.decode('utf-8'))
        self.assertSequenceEqual(results, ['editorial::editorial-core-base'])


class api_package_files_customTestCase(TestCase):
    """Unit tests for function :py:func:`~utl_files.views.api_package_files_custom`."""

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
            self.assertTrue(Package.objects.filter())
            response = views.api_package_files_custom(
                request,
                site_name,
                record["name"])
        json_out = response.getvalue().decode('utf-8')
        file_list = json.loads(json_out)
        self.assertNotIn('error', file_list)
        path_list = [finfo["path"] for finfo in file_list]
        self.assertSetEqual(set(self.TEST_FILES), set(path_list))


class api_packages_for_site_with_skinsTestCase(TestCaseMixin, TestCase):
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
        cls.certified_skin, _ = Package.objects.get_or_create(
            app=cls.app,
            last_download=datetime(2016, 3, 22, 17, 57, 23, tzinfo=pytz.utc),
            is_certified=True,
            disk_directory='certified/skins/editorial/editorial-core-advanced-mobile_1.54.0.0',
            name='editorial-core-advanced-mobile',
            pkg_type=Package.SKIN,
            site=None,
            version='1.54.0.0')

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
            self.assertDictContainsSubset(pkg_dict, expected)

    def test_w_used_by(self):
        """Unit test for
        :py:meth:`utl_files.views.api_packages_for_site_with_skins`, where
        the skin is a certified skin associated with the site by
        :py:class:`utl_files.models.CertifiedUsedBy`.

        """
        used_by, _ = CertifiedUsedBy.objects.get_or_create(site=self.tn_site,
                                                           package=self.certified_skin)
        try:
            request = make_wsgi_request("files/api_packages_for_site_with_skins/{}/{}/N/{}/{}/{}/"
                                        "".format(self.tn_site.domain,
                                                  self.GSKIN_NAME,
                                                  self.app.name,
                                                  self.certified_skin.name,
                                                  self.certified_skin.version))

            response = views.api_packages_for_site_with_skins(request, self.tn_site.domain,
                                                              self.GSKIN_NAME, self.app.name,
                                                              self.ASKIN_NAME)
            actual = json.loads(response.getvalue().decode('utf-8'))
            self.assertSetEqual({pkg["name"] for pkg in actual},
                                set([pkg.name for pkg in [self.global_skin, self.app_skin]]))

            response = views.api_packages_for_site_with_skins(request, self.tn_site.domain,
                                                              self.GSKIN_NAME, self.app.name,
                                                              self.certified_skin.name)
            actual = json.loads(response.getvalue().decode('utf-8'))
            self.assertSetEqual({pkg["name"] for pkg in actual},
                                set([pkg.name for pkg in
                                     [self.global_skin, self.certified_skin]]))
        finally:
            used_by.delete()

    def test_wout_used_by(self):
        """Unit test for :py:meth:`utl_files.views.api_packages_for_site_with_skins`, where the
        skin is a certified skin not associated with the site by
        :py:class:`~utl_files.models.CertifiedUsedBy`. In that case the view attempts to find a
        match anyway.

        """
        self.assertEqual(CertifiedUsedBy.objects.filter(site=self.tn_site,
                                                        package=self.certified_skin).count(),
                         0)
        request = make_wsgi_request("files/api_packages_for_site_with_skins/{}/{}/N/{}/{}/{}/"
                                    "".format(self.tn_site.domain,
                                              self.GSKIN_NAME,
                                              self.app.name,
                                              self.certified_skin.name,
                                              self.certified_skin.version))

        response = views.api_packages_for_site_with_skins(request, self.tn_site.domain,
                                                          self.GSKIN_NAME, self.app.name,
                                                          self.ASKIN_NAME)
        actual = json.loads(response.getvalue().decode('utf-8'))
        self.assertSetEqual({pkg["name"] for pkg in actual},
                            set([pkg.name for pkg in [self.global_skin, self.app_skin]]))

        response = views.api_packages_for_site_with_skins(request, self.tn_site.domain,
                                                          self.GSKIN_NAME, self.app.name,
                                                          self.certified_skin.name)
        actual = json.loads(response.getvalue().decode('utf-8'))
        self.assertSetEqual({pkg["name"] for pkg in actual},
                            set([pkg.name for pkg in
                                 [self.global_skin, self.certified_skin]]))

    def test_no_match(self):
        """Unit test for
        :py:meth:`utl_files.views.api_packages_for_site_with_skins`, where
        the skin can't be found.

        """
        request = make_wsgi_request("files/api_packages_for_site_with_skins/{}/{}/N/{}/{}/{}/"
                                    "".format(self.tn_site.domain,
                                              self.GSKIN_NAME,
                                              self.app.name,
                                              'some-bogus-skin-name',
                                              self.certified_skin.version))

        response = views.api_packages_for_site_with_skins(request, self.tn_site.domain,
                                                          self.GSKIN_NAME, self.app.name,
                                                          'some-bogus-skin-name')
        actual = json.loads(response.getvalue().decode('utf-8'))
        self.assertIn('error', actual)


class api_package_files_certifiedTestCase(TestCaseMixin, TestCase):
    """Unit tests for :py:func:`utl_files.views.api_package_files_certified`."""

    @classmethod
    def setUpTestData(cls):
        cls.paper, _ = NewsPaper.objects.get_or_create(name='Richmond Times-Dispatch')
        cls.tn_site, _ = TownnewsSite.objects.get_or_create(URL='http://richmond.com',
                                                            name='RTD',
                                                            paper=cls.paper)
        cls.app, _ = Application.objects.get_or_create(name="editorial")
        cls.gl_app, _ = Application.objects.get_or_create(name="global")
        simplefilter("ignore")
        # pesky detail required for Package.load_from()
        settings.TNPACKAGE_FILES_ROOT = str(Path('utl_files/test_data').absolute())
        cls.data_dir = Path('utl_files/test_data/certified/skins/'
                            'skin-editorial-core-base').absolute()
        try:
            cls.pkg = Package.load_from(cls.data_dir,
                                        cls.tn_site,
                                        Package.SKIN)
        finally:
            simplefilter("default")

    def test_basic_call(self):
        """Unit test for :py:meth:`utl_files.views.api_package_files_certified` with a single
        package returned.

        """
        url = 'api/package_files/certified/editorial-core-base/1.45.1.0/'
        request = make_wsgi_request(url)
        response = views.api_package_files_certified(request,
                                                     'editorial-core-base',
                                                     '1.45.1.0')
        actual = json.loads(response.getvalue().decode('utf-8'))
        self.assertNotIn('error', actual)
        self.assertEqual(len(actual), 142)
        expected = {'pkg_certified': True,
                    'pkg_download': '2016-06-09T19:46:25Z',
                    'pkg_name': 'editorial-core-base',
                    'pkg_site': 'http://richmond.com',
                    'pkg_version': '1.45.1.0'}
        for pkg_file in actual:
            self.assertDictContainsSubset(pkg_file, expected)
        actual_files = [pkg_file['path'] for pkg_file in actual]
        for actual_fname in actual_files:
            self.assertTrue((self.data_dir / actual_fname).exists())

    def test_no_version(self):
        """Unit test for :py:meth:`utl_files.views.api_package_files_certified` where the package
        name is specified but not the version.

        """
        url = 'api/package_files/certified/editorial-core-base/'
        request = make_wsgi_request(url)
        response = views.api_package_files_certified(request,
                                                     'editorial-core-base')
        actual = json.loads(response.getvalue().decode('utf-8'))
        self.assertNotIn('error', actual)
        self.assertEqual(len(actual), 142)
        expected = {'pkg_certified': True,
                    'pkg_download': '2016-06-09T19:46:25Z',
                    'pkg_name': 'editorial-core-base',
                    'pkg_site': 'http://richmond.com',
                    'pkg_version': '1.45.1.0'}
        for pkg_file in actual:
            self.assertDictContainsSubset(pkg_file, expected)
        actual_files = [pkg_file['path'] for pkg_file in actual]
        for actual_fname in actual_files:
            self.assertTrue((self.data_dir / actual_fname).exists())

    def test_multiple_found(self):
        """Unit test for :py:meth:`utl_files.views.api_package_files_certified` where the
        criteria specified match multiple packages.

        """
        the_pkg = Package.objects.get(name='editorial-core-base', version='1.45.1.0')
        new_pkg = Package(name=the_pkg.name,
                          version='1.52.1.0',
                          app=the_pkg.app,
                          is_certified=the_pkg.is_certified,
                          last_download=the_pkg.last_download,
                          site=the_pkg.site,
                          disk_directory=the_pkg.disk_directory,
                          pkg_type=the_pkg.pkg_type)
        new_pkg.full_clean()
        new_pkg.save()
        try:
            url = 'api/package_files/certified/editorial-core-base/'
            request = make_wsgi_request(url)
            response = views.api_package_files_certified(request,
                                                         'editorial-core-base')
            actual = json.loads(response.getvalue().decode('utf-8'))
            self.assertIn('error', actual)
            self.assertEqual(actual['error'], 404)
            self.assertIn('without version',
                          actual['message'])
        finally:
            new_pkg.delete()


class api_macros_for_site_with_skinsTestCase(TestCaseMixin, TestCase):
    """Unit tests for :py:func:`~utl_files.views.api_macros_for_site_with_skins`."""

    @classmethod
    def setUpTestData(cls):
        """Load test packages, files, macro defs for testing."""
        # nearly impossible to use fixtures when some data has been loaded
        # with data migrations, due to PK conflicts
        cls.the_site = TownnewsSite.objects.get(URL='http://kearneyhub.com')

        # TODO: Need a lot more data, incl. comps and blocks, other skins, etc.
        pkg_data = [{"name": "base-kh-oct-2013-1-ads",
                     "version": "1.14.2",
                     "is_certified": False,
                     "app": Application.objects.get(name="editorial"),
                     "last_download": datetime(2016, 6, 8, 20, 15, 49, 0, pytz.UTC),
                     "disk_directory": "kearneyhub.com/skins/editorial/base-kh-oct-2013-1-ads",
                     "pkg_type": Package.SKIN},
                    {"app": Application.objects.get(name="global"),
                     "disk_directory": "kearneyhub.com/global_skins/global-kh-oct-2013-dev",
                     "is_certified": False,
                     "last_download": datetime(2016, 6, 8, 20, 15, 49, 0, pytz.UTC),
                     "name": "global-kh-oct-2013-dev",
                     "pkg_type": Package.GLOBAL_SKIN,
                     "version": "0.1"},
                    {"app": Application.objects.get(name="global"),
                     "disk_directory": "kearneyhub.com/global_skins/global-dev",
                     "is_certified": False,
                     "last_download": datetime(2015, 12, 8, 20, 15, 49, 0, pytz.UTC),
                     "name": "global-dev",
                     "pkg_type": Package.GLOBAL_SKIN,
                     "version": "0.1"},
                    {"name": "base-core-kh-editorial",
                     "version": "1.2",
                     "is_certified": False,
                     "app": Application.objects.get(name="editorial"),
                     "last_download": datetime(2013, 6, 8, 20, 15, 49, 0, pytz.UTC),
                     "disk_directory": "kearneyhub.com/skins/editorial/base-core-kh-editorial",
                     "pkg_type": Package.SKIN}]

        files_data = [{"file_path": "includes/macros.inc.utl",
                       "pkg_name": "base-kh-oct-2013-1-ads", }]

        for datum in pkg_data:
            new_pkg = Package(site=cls.the_site,
                              name=datum["name"],
                              version=datum["version"],
                              app=datum["app"],
                              is_certified=datum["is_certified"],
                              last_download=datum["last_download"],
                              pkg_type=datum["pkg_type"])
            new_pkg.full_clean()
            new_pkg.save()

        for datum in files_data:
            new_file = UTLFile(pkg=Package.objects.get(name=datum["pkg_name"]),
                               file_path=datum["file_path"])
            new_file.full_clean()
            new_file.save()

        with open("utl_files/test_data/api_macros_for_site_with_skins_test.json", "r") as mdefin:
            mdef_data = json.load(mdefin)
            for ufile_datum in mdef_data:
                the_pkg = Package.objects.get(site=cls.the_site,
                                              name=ufile_datum["pkg_name"])
                the_file = UTLFile.objects.get(pkg=the_pkg,
                                               file_path=ufile_datum["file_path"])
                for mdef_datum in ufile_datum["macro_defs"]:
                    new_mdef = MacroDefinition(
                        source=the_file,
                        text=mdef_datum['text'],
                        name=mdef_datum['name'],
                        start=mdef_datum['start'],
                        end=mdef_datum['end'],
                        line=mdef_datum['line'])
                    new_mdef.full_clean()
                    new_mdef.save()

    def test_success(self):
        """Test a normal successful call to the view."""
        site_name = 'kearneyhub.com'
        global_name = 'global-kh-oct-2013-dev'
        app_name = 'editorial'
        skin_name = 'base-kh-oct-2013-1-ads'
        request = make_wsgi_request("files/api/macros_for_site_with_skins/{}/{}/{}/{}/"
                                    "".format(site_name, global_name, app_name, skin_name))
        response = views.api_macros_for_site_with_skins(request, 'kearneyhub.com',
                                                        'global-kh-oct-2013-dev',
                                                        'editorial',
                                                        'base-kh-oct-2013-1-ads')
        isinstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        expected = {"archived_asset": {"line": 38, "end": 2070, "start": 1505, },
                    "bloxSelect": {"line": 102, "end": 3941, "start": 3610, },
                    "filterAssetByPosition": {"line": 205, "end": 7824, "start": 6898, },
                    "filterAssetBySubtype": {"line": 175, "end": 6865, "start": 5945, },
                    "filterAssetsBySection": {"line": 236, "end": 8574, "start": 7857, },
                    "filterImagesByPresentation": {"line": 141, "end": 5912, "start": 4807, },
                    "free_archive_period": {"line": 54, "end": 2742, "start": 2072, },
                    "ifAnonymousUser": {"line": 322, "end": 11728, "start": 11094, },
                    "thisSectionPath": {"line": 76, "end": 3092, "start": 2836, },
                    "youtubePlayer": {"line": 258, "end": 11032, "start": 8608, }}
        results = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(results), len(expected))
        for mdef in results:
            # some values should be same for all
            return_expected = {"file": "includes/macros.inc.utl",
                               "pkg_name": "base-kh-oct-2013-1-ads",
                               "pkg_version": "1.14.2",
                               'pkg_certified': False,
                               'pkg_download': '2016-06-08T20:15:49Z',
                               'pkg_site': 'http://kearneyhub.com'}

            self.assertDictContainsSubset(mdef, return_expected)

            # check for unexpected keys
            self.assertSetEqual(set(['id', 'name', 'start', 'end', 'line']),
                                # ^ expected, not same for different macros
                                # v actual results - fields that are same
                                set(mdef.keys()) - set(return_expected.keys()))
            # get the other expected values
            self.assertIn(mdef["name"], expected)
            exp_mdef = expected[mdef["name"]]
            self.assertDictContainsSubset(mdef, exp_mdef)


# class api_file_text_w_syntaxTestCase(MacroTestCase):

    # def test_markup(self):
        # # hardly the best way to test this, but at least will detect changes
        # for file in self.test_files:
            # html_name = Path(self.TEST_DIR) / "{}_mkup.html".format(file.pkg.name)
            # with html_name.open('r') as htmlin:
                # expected_text = htmlin.read()
            # actual_text = file.text_with_markup
            # # this won't work: order of tags not guaranteed. We need assertHTMLEqual()
            # self.assertEqual(actual_text, expected_text)


# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
