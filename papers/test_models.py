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
        item1 = TownnewsSite(URL=self.TEST_URL, name=self.TEST_NAME, paper=paper)
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
        item1 = TownnewsSite(URL=self.TEST_URL, name=self.TEST_NAME, paper=paper)
        self.assertEqual(item1.domain, 'toaddagger.com')

    def test_str(self):
        """Unit test for :py:meth:`~papers.models.TownnewsSite.__str__`."""
        for site in TownnewsSite.objects.all():
            if site.name:
                self.assertEqual(site.name, str(site))
            else:
                self.assertEqual(site.URL, str(site))


class NewsPaperTestCase(TestCase):
    """Unit test cases for :py:class:`papers.models.NewsPaper`."""

    def test_str(self):
        """Unit tests for :py:meth:`papers.models.NewsPaper.__str__`."""
        self.assertGreater(NewsPaper.objects.count(), 20)  # just to make sure we have test data
        for paper in NewsPaper.objects.all():
            self.assertEqual(str(paper), paper.name)
