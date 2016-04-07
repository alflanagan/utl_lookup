#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_files.views`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods,no-member,invalid-name
from copy import deepcopy
import json

from django.test import TestCase

from utl_files.views import api_global_skins_for_site, api_files_for_custom_pkg
from utl_files.models import Application, Package, UTLFile
from papers.models import NewsPaper, TownnewsSite


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
        response = api_global_skins_for_site(None, "richmond.com")
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
            response = api_files_for_custom_pkg(request, record["site"].replace('http://', ''),
                                                record["name"], record["last_download"])
        json_out = response.getvalue().decode('utf-8')
        file_list = json.loads(json_out)
        self.assertSetEqual(set(self.TEST_FILES), set(file_list))

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
