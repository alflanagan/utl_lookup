#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_files.views`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods,no-member

from django.test import TestCase, TransactionTestCase
from django.db.utils import DataError
from django.core.exceptions import ValidationError

from utl_files.views import api_global_skins_for_site


class api_global_skins_for_siteTestCase(TestCase):
    """Unit tests for class :py:class:`~utl_files.views.api_global_skins_for_site`."""

    def test_create(self):
        """Unit test for :py:meth:`utl_files.views.api_global_skins_for_site`."""
        item1 = api_global_skins_for_site(None, "http://richmond.com")


# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
