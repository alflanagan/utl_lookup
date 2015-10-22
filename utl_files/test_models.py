#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os

from django.test import TestCase, TransactionTestCase
from django.db.utils import DataError
from django.core.exceptions import ValidationError

from .models import Application, MacroDefinition, MacroRef, Package, PackageDep, PackageProp
from .models import PackageError, UTLFile, UTLFileError


class ApplicationTestCase(TestCase):
    """Unit tests for :py:class:`utl_files.models.Application`.

    There's not really anything to test here, but I like to validate basic assumptions so that
    if they change, I'm forced to update tests to match.

    """
    def setUp(self):
        """Create a simple Application record for testing."""
        app = Application(name="editorial")
        app.save()

    def test_insert(self):
        """Unit test for :py:meth:`utl_files.models.Application` and
        :py:meth:`utl_files.models.Application.save`.

        """
        self.assertEqual(Application.objects.count(), 1)
        the_app = Application.objects.all()[0]
        self.assertEqual(the_app.name, "editorial")

    def test_delete(self):
        """Unit test for :py:meth:`models.Application.delete`."""
        self.assertEqual(Application.objects.count(), 1)
        the_app = Application.objects.get(name="editorial")
        the_app.delete()
        self.assertEqual(Application.objects.count(), 0)
        self.assertRaises(Application.DoesNotExist, Application.objects.get, name="editorial")

    def test_bad(self):
        """Test that we get expected errors when name is too long."""
        bad_app = Application(name="x" * 80)
        self.assertRaises(DataError, bad_app.save)
        self.assertRaises(ValidationError, bad_app.full_clean)


class PackageTestCase(TransactionTestCase):
    """Unit tests for :py:class:`utl_files.models.Package`."""

    TEST_APP = "editorial"
    TEST_NAME = "some_totally_bogus_package"
    TEST_VERSION = "1.10.0.3"

    def setUp(self):
        """Create a package object for tests."""
        app = Application(name=self.TEST_APP)
        app.save()
        pkg = Package(name=self.TEST_NAME,
                      version=self.TEST_VERSION,
                      is_certified=True,
                      app=app)
        pkg.full_clean()
        pkg.save()

    def test_insert(self):
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

    TEST_APP = "editorial"
    TEST_PKG = "skin-editorial-core-base"
    TEST_VERSION = "1.45.1.0"
    PKG_DIRECTORY = "utl_files/test_data/skin-editorial-core-base"
    SIMPLE_UTL_FILE = "includes/footer-spotless.inc.utl"
    MACROS_FILE = "includes/macros.inc.utl"

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

    def test_full_file_path(self):
        self.assertEqual(str(self.simple_utl.full_file_path),
                         os.path.join(self.PKG_DIRECTORY, self.SIMPLE_UTL_FILE))

    def test_to_dict(self):
        self.assertDictEqual(self.simple_utl.to_dict(),
                             {'name': self.TEST_PKG,
                              'path': self.SIMPLE_UTL_FILE,
                              'pkg_directory': self.PKG_DIRECTORY,
                              'version': self.TEST_VERSION})

    def test_str(self):
        self.assertEqual(str(self.simple_utl), "{}/{}:{}".format(self.TEST_APP, self.TEST_PKG,
                                                                 self.SIMPLE_UTL_FILE))

    def test_get_macros_none(self):
        """Test that :py:meth:`utl_file.models.UTLFile.get_macros` can successfully do nothing."""
        self.simple_utl.get_macros()
        self.assertEqual(MacroDefinition.objects.count(), 0)
        self.assertEqual(MacroRef.objects.count(), 0)

    def test_get_macros_many(self):
        """Test that :py:meth:`utl_file.models.UTLFile.get_macros` can successfully load macros."""
        self.macros_utl.get_macros()
        self.assertEqual(MacroDefinition.objects.count(), 11)
        self.assertEqual(MacroRef.objects.count(), 14)

