#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lookup.papers.views`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
import re
from html import escape

# pylint: disable=too-few-public-methods
from django.test import TestCase

from papers.models import NewsPaper
from papers.views import index



class IndexTestCase(TestCase):
    """Unit tests for view :py:func:`~utl_lookup.papers.views.index`."""

    EXPECTED_STRINGS = [re.compile('<div class="row">'),
                        re.compile('<div class="dropdown">'),
                        re.compile(r'<button .* type="button"'),
                        re.compile('id="select_paper_btn"'),
                        re.compile('data-toggle="dropdown"'),
                        re.compile('<ul class="dropdown-menu" id="select_paper_menu"'),
                        re.compile('<li data-paper="[0-9]+"><a href="#">')]

    PAPER_REGEX = r'<li data-paper="[0-9]+"><a href="#">{}</a></li>'

    def test_create(self):
        """Unit test for :py:func:`papers.views.index`."""
        request = None
        response = index(request)
        html = response.getvalue().decode('utf-8')
        for expected in self.EXPECTED_STRINGS:
            match = expected.search(html)
            self.assertIsNotNone(match, expected.pattern)
        for paper in NewsPaper.objects.all():
            expected = '<li data-paper="{}"><a href="#">{}'.format(paper.id, escape(paper.name))
            self.assertIn(expected, html)

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
