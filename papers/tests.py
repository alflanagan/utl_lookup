#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for :py:mod:`papers.models`.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from django.test import TestCase

from papers.models import TownnewsSite, NewsPaper

# pylint: disable=no-member


class TownnewsSiteTestCase(TestCase):
    """Unit tests for class :py:class:`~papers.models.TownnewsSite`."""
    TEST_PAPER = 'The Royal Toad-Dagger'
    TEST_URL = 'http://toaddagger.com'
    TEST_NAME = 'RTD'

    def test_create(self):
        """Unit test for :py:meth:`papers.models.TownnewsSite`."""
        paper = NewsPaper(name=self.TEST_PAPER)
        paper.save()
        item1 = TownnewsSite(URL=self.TEST_URL,
                             name=self.TEST_NAME,
                             paper=paper)
        item1.full_clean()
        item1.save()
        readback = TownnewsSite.objects.get(URL=self.TEST_URL)
        self.assertIsNotNone(readback)
        self.assertEqual(readback.URL, self.TEST_URL)  # not really necessary
        self.assertEqual(readback.name, self.TEST_NAME)
        self.assertEqual(readback.paper.name, self.TEST_PAPER)

    def test_domain(self):
        """Unit test for :py:prop:`~papers.models.TownnewsSite.domain`."""
        paper = NewsPaper(name=self.TEST_PAPER)
        paper.save()
        item1 = TownnewsSite(URL=self.TEST_URL,
                             name=self.TEST_NAME,
                             paper=paper)
        self.assertEqual(item1.domain, 'toaddagger.com')
