#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lookup.papers.views`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
import re
from html import escape
import sys
import json
from io import StringIO
from wsgiref.util import FileWrapper

# pylint: disable=too-few-public-methods,no-member,invalid-name
from django.test import TestCase
from django.core.handlers.wsgi import WSGIRequest

from papers.models import NewsPaper, TownnewsSite
from papers import views


def make_wsgi_request(request_text):
    """Helper script, makes a :py:class:`WSGIRequest` object for the GET method retrieving
    `request_text`.

    """
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
               'HTTP_USER_AGENT':
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
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
    return WSGIRequest(environ)


class IndexTestCase(TestCase):
    """Unit tests for view :py:func:`~utl_lookup.papers.views.index`."""

    # problem with doing this as one large REGEX: if it fails, no way to tell where
    # the failure occurred
    EXPECTED_STRINGS = [re.compile('<div class="row">'),
                        re.compile('<div class="dropdown">'),
                        re.compile(r'<button .* type="button"'),
                        re.compile('id="select_paper_btn"'),
                        re.compile('data-toggle="dropdown"'),
                        re.compile('<ul class="dropdown-menu" id="select_paper_menu"'),
                        re.compile('<li data-paper="[0-9]+"><a href="#">')]  # yapf: disable

    PAPER_REGEX = r'<li data-paper="[0-9]+"><a href="#">{}</a></li>'

    def test_create(self):
        """Unit test for :py:func:`papers.views.index`."""
        request = None
        response = views.index(request)
        html = response.getvalue().decode('utf-8')
        for expected in self.EXPECTED_STRINGS:
            match = expected.search(html)
            self.assertIsNotNone(match, expected.pattern)
        for paper in NewsPaper.objects.all():
            expected = '<li data-paper="{}"><a href="#">{}'.format(paper.id, escape(paper.name))
            self.assertIn(expected, html)


class api_sites_TestCase(TestCase):
    """Unit tests for api/sites/ URLs."""

    def test_all(self):
        """Unit test for :py:func:`papers.views.api_sites` with no paper specified."""
        request = make_wsgi_request("sites/")
        response = views.api_sites(request)
        results = json.loads(response.content.decode('utf-8'))
        fast_lookup = {}
        for site_rcd in results:
            fast_lookup[site_rcd["URL"]] = site_rcd
        self.assertEqual(TownnewsSite.objects.count(), len(fast_lookup))
        for site in TownnewsSite.objects.all():
            self.assertDictEqual(fast_lookup[site.URL], {"URL": site.URL,
                                                         "name": site.name,
                                                         "paper": site.paper.name, })

    def test_paper(self):
        """Unit test for :py:func:`papers.views.api_sites` with a specified
        :py:class:`papers.models.NewsPaper` name.

        """
        request = make_wsgi_request("api/sites/Richmond%20Times-Dispatch")
        response = views.api_sites(request, paper="Richmond Times-Dispatch")
        results = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(results), 1)
        self.assertDictEqual(results[0], {'paper': 'Richmond Times-Dispatch',
                                          'name': 'RTD',
                                          'URL': 'http://richmond.com'})

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
