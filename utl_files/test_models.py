#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Module of tests for :py:mod:`utl_files.models`."""

import os
import sys

from django.test import TestCase, TransactionTestCase
from django.db.utils import DataError
from django.core.exceptions import ValidationError

from .models import Application, MacroDefinition, MacroRef, Package, PackageDep, PackageProp
from .models import PackageError, UTLFile, UTLFileError
from papers.models import TownnewsSite, NewsPaper

# pylint: disable=no-member


class ApplicationTestCase(TestCase):
    """Unit tests for :py:class:`utl_files.models.Application`.

    There's not really anything to test here, but I like to validate basic assumptions so that
    if they change, I'm forced to update tests to match.

    """
    def setUp(self):
        """Create a simple Application record for testing."""
        if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 5):
            sys.stderr.write("This code requires python with a minimum version of 3.5.\n")
            sys.stderr.write("(Did you try running it with the 'python3' command?)\n")
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
        self.assertRaises(Application.DoesNotExist, Application.objects.get, name="testing")

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
        app = Application(name=self.TEST_APP)
        app.save()

        try:
            paper = NewsPaper.objects.get(name='Richmond Times-Dispatch')
        except NewsPaper.DoesNotExist:
            paper = NewsPaper(name='Richmond Times-Dispatch')
            paper.full_clean()
            paper.save()

        try:
            thesite = TownnewsSite.objects.get(URL='http://richmond.com')
        except TownnewsSite.DoesNotExist:
            thesite = TownnewsSite(URL='http://richmond.com', name='RTD', paper=paper)
            thesite.full_clean()
            thesite.save()

        pkg = Package(name=self.TEST_NAME,
                      version=self.TEST_VERSION,
                      is_certified=True,
                      app=app,
                      last_download="2015-05-01 13:00:00Z",
                      disk_directory="/data/exported/richmond.com/skins/testing/some_totally_bogus_package",
                      site=thesite,
                      pkg_type=Package.SKIN
                      )
        pkg.full_clean()
        pkg.save()

    def test_insert(self):
        """Unit test of :py:meth:`Package.save` (executed in :py:meth:`setUp`)"""
        self.assertEqual(Package.objects.count(), 1)
        pkg = Package.objects.get(name=self.TEST_NAME, version=self.TEST_VERSION)
        self.assertEqual(pkg.name, self.TEST_NAME)
        self.assertEqual(pkg.version, self.TEST_VERSION)
        self.assertEqual(pkg.app.name, self.TEST_APP)
        self.assertEqual(pkg.is_certified, True)

    def test_delete(self):
        pkg = Package.objects.get(name=self.TEST_NAME, version=self.TEST_VERSION)
        pkg.delete()
        self.assertEqual(Package.objects.count(), 0)
        self.assertRaises(Package.DoesNotExist, Package.objects.get,
                          name=self.TEST_NAME, version=self.TEST_VERSION)

    def test_bad(self):
        app = Application.objects.first()
        pkg = Package(name=self.TEST_NAME*20,
                      version=self.TEST_VERSION,
                      is_certified=True,
                      app=app)
        self.assertRaises(DataError, pkg.save)
        self.assertRaises(ValidationError, pkg.full_clean)

        pkg = Package(name=self.TEST_NAME,
                      version=self.TEST_VERSION*5,
                      is_certified=False,
                      app=app)
        self.assertRaises(DataError, pkg.save)
        self.assertRaises(ValidationError, pkg.full_clean)


class UTLFileTestCase(TransactionTestCase):
    """Unit tests for :py:class:`models.UTLFile`."""

    TEST_APP = "editorial"
    TEST_PKG = "skin-editorial-core-base"
    TEST_VERSION = "1.45.1.0"
    PKG_DIRECTORY = "utl_files/test_data/skin-editorial-core-base"
    SIMPLE_UTL_FILE = "includes/footer-spotless.inc.utl"
    MACROS_FILE = "includes/macros.inc.utl"
    macro_file_text = ""

    def setUp(self):
        self.app = Application(name=self.TEST_APP)
        self.app.save()
        self.pkg = Package(name=self.TEST_PKG,
                           version=self.TEST_VERSION,
                           is_certified=True,
                           app=self.app)
        self.pkg.save()
        # one of the simplest UTL files in the test data
        self.simple_utl = UTLFile(file_path=self.SIMPLE_UTL_FILE,
                                  pkg_directory=self.PKG_DIRECTORY,
                                  pkg=self.pkg)
        self.simple_utl.save()
        self.macros_utl = UTLFile(file_path=self.MACROS_FILE,
                                  pkg_directory=self.PKG_DIRECTORY,
                                  pkg=self.pkg)
        self.macros_utl.save()

    def test_create(self):
        self.assertEqual(UTLFile.objects.count(), 2)
        thefile = UTLFile.objects.get(file_path=self.SIMPLE_UTL_FILE)
        self.assertEqual(thefile.file_path, self.SIMPLE_UTL_FILE)
        self.assertEqual(thefile.pkg_directory, self.PKG_DIRECTORY)
        self.assertEqual(thefile.pkg, self.pkg)
        self.assertEqual(thefile.base_filename, os.path.basename(self.SIMPLE_UTL_FILE))

    def test_full_file_path(self):
        """:py:meth:`utl_file.models.UTLFile instance has attribute `full_file_path`."""
        self.assertEqual(str(self.simple_utl.full_file_path),
                         os.path.join(self.PKG_DIRECTORY, self.SIMPLE_UTL_FILE))

    def test_to_dict(self):
        """:py:meth:`utl_file.models.UTLFile instance can convert to :py:class:`dict`."""
        # assertDictContainsSubset is deprecated because args are in wrong order,
        # but we'll keept this until a good replacement comes along
        self.assertDictContainsSubset({'name': self.TEST_PKG,
                                       'path': self.SIMPLE_UTL_FILE,
                                       'pkg_directory': self.PKG_DIRECTORY,
                                       'version': self.TEST_VERSION},
                                      self.simple_utl.to_dict())
        # don't in general know what ID was assigned, just that there is one
        self.assertIn("id", self.simple_utl.to_dict())

    def test_str(self):
        """:py:meth:`utl_file.models.UTLFile instance can convert to :py:class:`str`."""
        self.assertEqual(str(self.simple_utl), "{}/{}:{}".format(self.TEST_APP, self.TEST_PKG,
                                                                 self.SIMPLE_UTL_FILE))

    def test_get_macros_none(self):
        """:py:meth:`utl_file.models.UTLFile.get_macros` can successfully do nothing."""
        self.simple_utl.get_macros()
        self.assertEqual(MacroDefinition.objects.count(), 0)
        self.assertEqual(MacroRef.objects.count(), 0)

    def _verify_macro(self, macro_name, line, start, end):
        macro_rcd = MacroDefinition.objects.get(name=macro_name)
        self.assertEqual(macro_rcd.source, self.macros_utl)
        self.assertEqual(macro_rcd.line, line)
        self.assertEqual(macro_rcd.start, start)
        self.assertEqual(macro_rcd.end, end)
        if not self.macro_file_text:
            with open(os.path.join(self.PKG_DIRECTORY, self.MACROS_FILE), 'r') as macin:
                self.macro_file_text = macin.read()
        self.assertEqual(macro_rcd.text, self.macro_file_text[start:end])

    def test_get_macros_many(self):
        """:py:meth:`utl_file.models.UTLFile.get_macros` can successfully load macros."""
        self.macros_utl.get_macros()
        self.assertEqual(MacroDefinition.objects.count(), 11)
        self.assertEqual(MacroRef.objects.count(), 14)
        self._verify_macro("archived_asset", 38, 1504, 2069)
        self._verify_macro("free_archive_period", 54, 2071, 2741)
        self._verify_macro("ifAnonymousUser", 356, 12033, 12667)  # last one in file
