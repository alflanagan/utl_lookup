#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`code_markup`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods

import unittest
from django.test import TestCase

from utl_files.code_markup import UTLWithMarkup


class UTLWithMarkupTestCase(TestCase):
    """Unit tests for class :py:class:`~code_markup.UTLWithMarkup`."""

    def test_create(self):
        """Unit test for :py:meth:`code_markup.UTLWithMarkup`."""
        item1 = UTLWithMarkup('[% if fred==wilma echo "barney"; %]')
        self.assertEqual(item1.source, '[% if fred==wilma echo "barney"; %]')


if __name__ == '__main__':
    unittest.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
