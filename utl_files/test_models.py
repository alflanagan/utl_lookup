#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Module of tests for :py:mod:`utl_files.models`."""

import os
import sys

from django.test import TestCase, TransactionTestCase
from django.db.utils import DataError
from django.core.exceptions import ValidationError

from .models import Application, MacroDefinition, MacroRef, Package
from .models import UTLFile
from papers.models import TownnewsSite, NewsPaper

# pylint: disable=no-member,invalid-name


class ApplicationTestCase(TestCase):
    """Unit tests for :py:class:`utl_files.models.Application`.

    There's not really anything to test here, but I like to validate basic assumptions so that
    if they change, I'm forced to update tests to match.

    """

    def setUp(self):
        """Create a simple Application record for testing."""
        if sys.version_info.major < 3 or (sys.version_info.major == 3 and
                                          sys.version_info.minor < 5):
            sys.stderr.write(
                "This code requires python with a minimum version of 3.5.\n")
            sys.stderr.write(
                "(Did you try running it with the 'python3' command?)\n")
            sys.exit(2)
        app = Application(name="testing")
        app.save()

    def test_insert(self):
        """Unit test for :py:meth:`utl_files.models.Application` and
        :py:meth:`utl_files.models.Application.save`.

        """
        the_app = Application.objects.get(name="testing")
        self.assertEqual(the_app.name, "testing")

    def test_delete(self):
        """Unit test for :py:meth:`models.Application.delete`."""
        count_before = Application.objects.count()
        the_app = Application.objects.get(name="testing")
        the_app.delete()
        self.assertEqual(Application.objects.count(), count_before - 1)
        self.assertRaises(Application.DoesNotExist,
                          Application.objects.get,
                          name="testing")

    def test_bad(self):
        """Test that we get expected errors when name is too long."""
        bad_app = Application(name="x" * 80)
        self.assertRaises(DataError, bad_app.save)
        self.assertRaises(ValidationError, bad_app.full_clean)


class PackageTestCase(TransactionTestCase):
    """Unit tests for :py:class:`utl_files.models.Package`."""

    TEST_APP = "testing"
    TEST_NAME = "some_totally_bogus_package"
    TEST_VERSION = "1.10.0.3"

    def setUp(self):
        """Create a package object for tests."""
        self.test_app = Application(name=self.TEST_APP)
        self.test_app.save()

        try:
            paper = NewsPaper.objects.get(name='Richmond Times-Dispatch')
        except NewsPaper.DoesNotExist:
            paper = NewsPaper(name='Richmond Times-Dispatch')
            paper.full_clean()
            paper.save()

        try:
            thesite = TownnewsSite.objects.get(URL='http://richmond.com')
        except TownnewsSite.DoesNotExist:
            thesite = TownnewsSite(URL='http://richmond.com',
                                   name='RTD',
                                   paper=paper)
            thesite.full_clean()
            thesite.save()
        self.test_site = thesite

        pkg = Package(
            name=self.TEST_NAME,
            version=self.TEST_VERSION,
            is_certified=True,
            app=self.test_app,
            last_download="2015-05-01 13:00:00Z",
            disk_directory=("/data/exported/richmond.com/skins/testing/"
                            "some_totally_bogus_package"),
            site=thesite,
            pkg_type=Package.SKIN)
        pkg.full_clean()
        pkg.save()

    def test_insert(self):
        """Unit test of :py:meth:`Package.save` (executed in :py:meth:`setUp`)"""
        self.assertEqual(Package.objects.count(), 1)
        pkg = Package.objects.get(name=self.TEST_NAME,
                                  version=self.TEST_VERSION)
        self.assertEqual(pkg.name, self.TEST_NAME)
        self.assertEqual(pkg.version, self.TEST_VERSION)
        self.assertEqual(pkg.app.name, self.TEST_APP)
        self.assertEqual(pkg.is_certified, True)

    def test_delete(self):
        """Unit test of deletion of :py:class:`~utl_files.models.Package` object."""
        pkg = Package(name='short-lived-pkg',
                      version=self.TEST_VERSION,
                      is_certified=False,
                      app=self.test_app,
                      last_download='2016-07-22 19:03Z',
                      site=self.test_site,
                      pkg_type=Package.COMPONENT)
        pkg.full_clean()
        pkg.save()
        pkg = Package.objects.get(name='short-lived-pkg',
                                  version=self.TEST_VERSION)
        pkg.delete()
        self.assertEqual(Package.objects.count(), 1)
        self.assertRaises(Package.DoesNotExist,
                          Package.objects.get,
                          name='short-lived-pkg',
                          version=self.TEST_VERSION)

    def test_bad(self):
        """Unit tests for failure modes in :py:meth:`~utl_files.models.Package`."""
        app = Application.objects.first()
        pkg = Package(name=self.TEST_NAME * 20,
                      version=self.TEST_VERSION,
                      is_certified=True,
                      app=app)
        self.assertRaises(DataError, pkg.save)
        self.assertRaises(ValidationError, pkg.full_clean)

        pkg = Package(name=self.TEST_NAME,
                      version=self.TEST_VERSION * 5,
                      is_certified=False,
                      app=app)
        self.assertRaises(DataError, pkg.save)
        self.assertRaises(ValidationError, pkg.full_clean)


class UTLFileTestCase(TestCase):
    """Unit tests for :py:class:`models.UTLFile`."""

    TEST_APP = "editorial"
    TEST_PKG = "skin-editorial-core-base"
    TEST_VERSION = "1.45.1.0"
    PKG_DIRECTORY = "utl_files/test_data/skin-editorial-core-base"
    SIMPLE_UTL_FILE = "includes/footer-spotless.inc.utl"
    MACROS_FILE = "includes/macros.inc.utl"
    macro_file_text = ""

    @classmethod
    def setUpTestData(cls):
        # if I make PKG_DIRECTORY absolute, it won't work on other systems. But, if it's
        # relative, it won't work if we're in the wrong directory. So, as a non-solution:
        if not os.path.isdir(cls.PKG_DIRECTORY):
            raise Exception(
                "Test data not found. UTLFileTestCase must be run from project root"
                " directory (location of manage.py).")

        cls.app = Application.objects.get(name='editorial')
        cls.pkg = Package(name=cls.TEST_PKG,
                          version=cls.TEST_VERSION,
                          is_certified=True,
                          app=cls.app,
                          disk_directory=cls.PKG_DIRECTORY)
        cls.pkg.save()
        # one of the simplest UTL files in the test data
        cls.simple_utl = UTLFile(file_path=cls.SIMPLE_UTL_FILE, pkg=cls.pkg)
        cls.simple_utl.save()
        cls.macros_utl = UTLFile(file_path=cls.MACROS_FILE, pkg=cls.pkg)
        cls.macros_utl.save()

    def test_create(self):
        """Unit test for :py:meth:`~utl_files.models.UTLFile`."""
        self.assertEqual(UTLFile.objects.count(), 2)
        thefile = UTLFile.objects.get(file_path=self.SIMPLE_UTL_FILE)
        self.assertEqual(thefile.file_path, self.SIMPLE_UTL_FILE)
        self.assertEqual(thefile.pkg, self.pkg)

    def test_base_filename(self):
        """Unit test for :py:meth:`~utl_files.models.UTLFile.base_filename`."""
        self.assertEqual(UTLFile.objects.count(), 2)
        thefile = UTLFile.objects.get(file_path=self.SIMPLE_UTL_FILE)
        self.assertEqual(thefile.base_filename,
                         os.path.basename(self.SIMPLE_UTL_FILE))

    def test_full_file_path(self):
        """:py:meth:`utl_file.models.UTLFile instance has attribute `full_file_path`."""
        self.assertEqual(
            str(self.simple_utl.full_file_path),
            os.path.join(self.PKG_DIRECTORY, self.SIMPLE_UTL_FILE))

    def test_to_dict(self):
        """:py:meth:`utl_file.models.UTLFile instance can convert to :py:class:`dict`."""
        self.assertDictEqual(
            {'path': 'includes/footer-spotless.inc.utl',
             'id': self.simple_utl.id,
             'package': self.pkg.id, }, self.simple_utl.to_dict())

    def test_str(self):
        """:py:meth:`utl_file.models.UTLFile instance can convert to :py:class:`str`."""
        self.assertEqual(
            str(self.simple_utl), "{}/{}:{}".format(
                self.TEST_APP, self.TEST_PKG, self.SIMPLE_UTL_FILE))

    def test_get_macros_none(self):
        """:py:meth:`utl_file.models.UTLFile.get_macros` can successfully do nothing."""
        self.simple_utl.get_macros()
        self.assertEqual(MacroDefinition.objects.count(), 0)
        self.assertEqual(MacroRef.objects.count(), 0)

    def _verify_macro(self, macro_name, line, start, end):
        """Helper method to compare :py:class:`~utl_files.models.MacroDefinition` object to
        expected values.

        """
        macro_rcd = MacroDefinition.objects.get(name=macro_name)
        self.assertEqual(macro_rcd.source, self.macros_utl)
        self.assertEqual(macro_rcd.line, line)
        self.assertEqual(macro_rcd.start, start)
        self.assertEqual(macro_rcd.end, end)
        if not self.macro_file_text:
            with open(
                    os.path.join(self.PKG_DIRECTORY,
                                 self.MACROS_FILE), 'r') as macin:
                self.macro_file_text = macin.read()
        self.assertEqual(macro_rcd.text, self.macro_file_text[start:end])

    def test_get_macros_many(self):
        """:py:meth:`utl_file.models.UTLFile.get_macros` can successfully load macros."""
        self.macros_utl.get_macros()
        self.assertEqual(MacroDefinition.objects.count(), 11)
        self.assertEqual(MacroRef.objects.count(), 14)
        self._verify_macro("archived_asset", 38, 1504, 2069)
        self._verify_macro("free_archive_period", 54, 2071, 2741)
        self._verify_macro("ifAnonymousUser", 356, 12033,
                           12667)  # last one in file
