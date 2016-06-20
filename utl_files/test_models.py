#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Module of tests for :py:mod:`utl_files.models`."""

import sys
import re
from pathlib import Path
from warnings import simplefilter
from datetime import datetime

from django.utils import timezone
from django.test import TestCase, TransactionTestCase
from django.db.utils import DataError
from django.core.exceptions import ValidationError
from django.conf import settings

from testplus.mock_objects import MockStream

from utl_files.models import (Application, MacroDefinition, MacroRef, Package, UTLFile,
                              UTLFileImportError, PackageError, PackageProp, PackageDep)
from papers.models import TownnewsSite, NewsPaper, TownnewsSiteMetaData

# pylint: disable=no-member,invalid-name


class ApplicationTestCase(TestCase):
    """Unit tests for :py:class:`utl_files.models.Application`.

    There's not really anything to test here, but I like to validate basic assumptions so that
    if they change, I'm forced to update tests to match.

    """

    # pylint: disable=R0201
    def setUp(self):
        """Create a simple Application record for testing."""
        if sys.version_info.major < 3 or (sys.version_info.major == 3 and
                                          sys.version_info.minor < 5):
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

    def test_to_dict(self):
        """Unit tests for :py:meth:`utl_files.models.Application.to_dict'.`"""
        self.assertGreater(Application.objects.count(), 10)
        for app in Application.objects.all():
            appdict = app.to_dict()
            self.assertIn('id', appdict)
            self.assertEqual(app.name, appdict['name'])


class PackageTestCase(TransactionTestCase):
    """Unit tests for :py:class:`utl_files.models.Package`."""

    TEST_APP = "testing"
    TEST_NAME = "some_totally_bogus_package"
    TEST_VERSION = "1.10.0.3"

    TEST_PKG = "editorial-core-base"
    PKG_DIRECTORY = "certified/skins/skin-editorial-core-base"

    UNCERT_PKG = "custom-newsletter-antwort-columns"
    UNCERT_SITE = "omaha.com"
    UNCERT_DIR = "omaha.com/skins/custom-newsletter-antwort-columns_0.15"

    ERROR_PKG_DIR = "dothaneagle.com/skins/editorial/custom-newsletter-2_1.9.11"

    @staticmethod
    def find_record_or_create(model_class, *_, **kwargs):
        """Attempt to use `kwargs` to retrieve an object from `model_class`. If object does not
        exist, attempt to create it, again using values in `kwargs`.

        """
        try:
            item = model_class.objects.get(**kwargs)
        except model_class.DoesNotExist:
            item = model_class(**kwargs)
            item.full_clean()
            item.save()
        return item

    def setUp(self):
        """Create package objects for tests."""
        self.global_app = self.find_record_or_create(Application, name="global")
        self.find_record_or_create(Application, name='editorial')
        # there's an assertWarns(), but not assertDoesNotWarn(). work-around by making warnings
        # into errors by default.
        simplefilter('error')

        self.test_app = Application(name=self.TEST_APP)
        self.test_app.full_clean()
        self.test_app.save()

        self.paper = self.find_record_or_create(NewsPaper, name='Richmond Times-Dispatch')
        self.paper2 = self.find_record_or_create(NewsPaper, name='Omaha World-Herald')
        self.test_site = self.find_record_or_create(TownnewsSite,
                                                    URL='http://richmond.com',
                                                    name='RTD',
                                                    paper=self.paper)
        self.test_site2 = self.find_record_or_create(TownnewsSite,
                                                     URL='http://omaha.com',
                                                     name='omaha.com',
                                                     paper=self.paper2)

        self.metadata = [TownnewsSiteMetaData(site=self.test_site,
                                              pkg_name='some-totally-bogus-package',
                                              zip_name="some_totally_bogus_package.zip",
                                              version=self.TEST_VERSION,
                                              is_certified=False,
                                              last_download="2015-05-01 13:00:00Z"),
                         TownnewsSiteMetaData(site=self.test_site,
                                              pkg_name=self.TEST_NAME,
                                              zip_name='pakcage_not_in_db.zip',
                                              version=self.TEST_VERSION,
                                              is_certified=False,
                                              last_download="2015-05-01 13:00:00Z"),
                         TownnewsSiteMetaData(site=self.test_site,
                                              pkg_name='certified-not-in-db',
                                              zip_name='core-asset-something.zip',
                                              version='2.17',
                                              is_certified=True,
                                              last_download="2015-05-01 13:00:00Z")]

        for mdata in self.metadata:
            mdata.full_clean()
            mdata.save()

        # load files from our test directory, not system directory
        settings.TNPACKAGE_FILES_ROOT = str(Path('.').resolve() / Path('utl_files/test_data'))

        # certified, non-global
        pkg = Package(name=self.TEST_NAME,
                      version=self.TEST_VERSION,
                      is_certified=True,
                      app=self.test_app,
                      last_download="2015-05-01 13:00:00Z",
                      disk_directory=("/data/exported/richmond.com/skins/testing/"
                                      "some_totally_bogus_package"),
                      site=self.test_site,
                      pkg_type=Package.SKIN)
        pkg.full_clean()
        pkg.save()
        # certified, global
        pkg2 = Package(name='another-totally-bogus-package',
                       version='2.1.7',
                       is_certified=True,
                       app=self.global_app,
                       last_download="2015-05-01 13:00:00Z",
                       disk_directory=("/data/exported/richmond.com/skins/testing/"
                                       "some_totally_bogus_package"),
                       site=self.test_site,
                       pkg_type=Package.SKIN)
        pkg2.full_clean()
        pkg2.save()
        # non-certified, non-global
        pkg3 = Package(name='custom-not-global-pkg',
                       version=self.TEST_VERSION,
                       is_certified=False,
                       app=self.test_app,
                       last_download="2015-05-01 13:00:00Z",
                       disk_directory=("/data/exported/richmond.com/skins/testing/"
                                       "some_totally_bogus_package"),
                       site=self.test_site,
                       pkg_type=Package.SKIN)
        pkg3.full_clean()
        pkg3.save()
        # non-certified, global
        pkg4 = Package(name='custom-and-global-pkg',
                       version=self.TEST_VERSION,
                       is_certified=False,
                       app=self.global_app,
                       last_download="2015-05-01 13:00:00Z",
                       disk_directory=("/data/exported/richmond.com/skins/testing/"
                                       "some_totally_bogus_package"),
                       site=self.test_site,
                       pkg_type=Package.SKIN)
        pkg4.full_clean()
        pkg4.save()

    def test_insert(self):
        """Unit test of :py:meth:`Package.save` (executed in :py:meth:`setUp`)"""
        pkg = Package.objects.get(name=self.TEST_NAME, version=self.TEST_VERSION)
        self.assertEqual(pkg.name, self.TEST_NAME)
        self.assertEqual(pkg.version, self.TEST_VERSION)
        self.assertEqual(pkg.app.name, self.TEST_APP)
        self.assertEqual(pkg.is_certified, True)

    def test_delete(self):
        """Unit test of deletion of :py:class:`~utl_files.models.Package` object."""
        original_count = Package.objects.count()
        pkg = Package(name='short-lived-pkg',
                      version=self.TEST_VERSION,
                      is_certified=False,
                      app=self.test_app,
                      last_download='2016-07-22 19:03Z',
                      site=self.test_site,
                      pkg_type=Package.COMPONENT)
        pkg.full_clean()
        pkg.save()
        pkg = Package.objects.get(name='short-lived-pkg', version=self.TEST_VERSION)
        pkg.delete()
        self.assertEqual(Package.objects.count(), original_count)
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
        self.assertRaises(ValidationError, pkg.full_clean, exclude=["is_certified"])
        self.assertRaises(ValidationError, pkg.full_clean, exclude=["site"])

    def test_errors(self):
        """Unit tests for :py:class:`utl_files.models.Package` error cases."""
        dup_certified_pkg = Package(name=self.TEST_NAME,
                                    version=self.TEST_VERSION,
                                    is_certified=True,
                                    app=self.test_app,
                                    last_download="2015-05-01 13:00:00Z",
                                    disk_directory=("/data/exported/richmond.com/skins/testing/"
                                                    "some_totally_bogus_package"),
                                    site=self.test_site,
                                    pkg_type=Package.SKIN)
        self.assertRaises(ValidationError, dup_certified_pkg.full_clean)
        # create package which duplicates existing record only in fields that are part of PK
        new_app = Application(name='error-test')
        new_app.full_clean()
        new_app.save()
        try:
            non_cert_pkg = Package(name=self.TEST_NAME,
                                   version='1.3',
                                   is_certified=False,
                                   app=new_app,
                                   last_download="2015-05-01 13:00:00Z",
                                   disk_directory=("/should/be/different/for/test"),
                                   site=self.test_site,
                                   pkg_type=Package.COMPONENT)
            # then try to validate it
            self.assertRaises(ValidationError, non_cert_pkg.full_clean)
        finally:
            new_app.delete()

    def test_str(self):
        """Unit test for :py:meth:`~utl_files.models.Package.__str__`."""
        for pkg in Package.objects.all():
            tstamp = ""
            if pkg.last_download:
                tstamp = pkg.last_download.strftime('%Y-%m-%d %H:%M')
            if pkg.is_certified:
                if pkg.app.name == 'global':
                    self.assertEqual(str(pkg),
                                     "certified/{}/{}".format(pkg.name, pkg.version))
                else:
                    self.assertEqual(str(pkg),
                                     "certified/{}::{}/{}".format(pkg.app, pkg.name, pkg.version))
            else:
                if pkg.app.name == 'global':
                    self.assertEqual(str(pkg),
                                     "{}/{}({})".format(pkg.site, pkg.name,
                                                        tstamp))
                else:
                    self.assertEqual(str(pkg),
                                     "{}/{}::{}({})".format(pkg.site, pkg.app, pkg.name,
                                                            tstamp))

    def test_to_dict(self):
        """Unit test for :py:meth:`~utl_files.models.Package.to_dict`."""
        for pkg in Package.objects.all():
            pkgdict = pkg.to_dict()
            self.assertSetEqual(
                set(pkgdict.keys()), set(["id", "app", "name", "version", "is_certified",
                                          "downloaded", "pkg_type", "location", "site"]))
            self.assertEqual(pkgdict["id"], pkg.id)
            self.assertEqual(pkgdict["app"], pkg.app.name)
            self.assertEqual(pkgdict["name"], pkg.name)
            self.assertEqual(pkgdict["version"], pkg.version)
            self.assertEqual(pkgdict["is_certified"], 'y' if pkg.is_certified else 'n')
            self.assertEqual(pkgdict["downloaded"], pkg.last_download)
            self.assertEqual(pkgdict["pkg_type"], pkg.pkg_type)
            self.assertEqual(pkgdict["location"], pkg.disk_directory)
            self.assertIn(pkg.site.URL, [self.test_site.URL, self.test_site2.URL])

    def test_load_from_certified(self):
        """Unit tests for :py:meth:`utl_files.models.Package.load_from(directory)`."""
        full_load_path = Path(settings.TNPACKAGE_FILES_ROOT) / Path(self.PKG_DIRECTORY)
        the_pkg = Package.load_from(full_load_path, self.test_site, Package.SKIN)
        self.assertEqual(the_pkg.name, self.TEST_PKG)
        self.assertRaises(ValueError, Package.load_from, full_load_path, self.test_site,
                          'NoSuchType')

    def test_load_from_non_cert(self):
        """Unit tests for :py:meth:`utl_files.models.Package.load_from(directory)` when package
        is non-certified, loads meta info.

        """
        full_load_path = Path(settings.TNPACKAGE_FILES_ROOT) / Path(self.UNCERT_DIR)
        the_pkg = Package.load_from(full_load_path, self.test_site2, Package.SKIN)
        self.assertEqual(the_pkg.name, self.UNCERT_PKG)

    def test_load_from_failure(self):
        """Unit tests for :py:meth:`utl_files.models.Package.load_from(directory)` error cases."""

        the_site = self.find_record_or_create(TownnewsSite,
                                              URL='http://dothaneagle.com',
                                              name='The Dothan Eagle',
                                              paper=self.paper2)
        full_load_path = Path(settings.TNPACKAGE_FILES_ROOT) / Path(self.ERROR_PKG_DIR)
        self.assertRaises(UserWarning, Package.load_from, full_load_path, the_site, Package.SKIN)
        site_meta_file = Path(settings.TNPACKAGE_FILES_ROOT) / 'dothaneagle.com/site_meta.json'
        self.assertFalse(site_meta_file.exists())
        Application.objects.get(name='editorial').delete()
        full_load_path = Path(settings.TNPACKAGE_FILES_ROOT) / Path(self.UNCERT_DIR)
        self.assertRaises(UTLFileImportError, Package.load_from, full_load_path, self.test_site2,
                          Package.SKIN)
        full_load_path = Path(settings.TNPACKAGE_FILES_ROOT) / Path(self.UNCERT_DIR)
        editorial = Application(name='editorial')
        editorial.save()
        the_pkg = Package.load_from(full_load_path, self.test_site2, Package.SKIN)
        the_pkg.disk_directory = "no_such_dir"
        self.assertRaises(PackageError, the_pkg.get_utl_files)

    def test_find_packages_for(self):
        """Unit tests for :py:meth:`~utl_files.models.Pakage.find_packages_for`"""
        pkgs = list(Package.find_packages_for(self.test_site, 'fred'))
        self.assertListEqual(pkgs, [])
        pkgs = list(Package.find_packages_for(self.test_site, self.TEST_NAME))
        self.assertEqual(len(pkgs), 1)
        pkgs = list(Package.find_packages_for(self.test_site.URL, self.TEST_NAME))
        self.assertEqual(len(pkgs), 1)
        pkgs = list(Package.find_packages_for(self.test_site.URL,
                                              'certified-not-in-db'))
        self.assertListEqual(pkgs, [])


class UTLFileTestCase(TestCase):
    """Unit tests for :py:class:`models.UTLFile`."""

    TEST_APP = "editorial"
    TEST_PKG = "skin-editorial-core-base"
    TEST_VERSION = "1.45.1.0"
    PKG_DIRECTORY = "certified/skins/skin-editorial-core-base"
    SIMPLE_UTL_FILE = "includes/footer-spotless.inc.utl"
    MACROS_FILE = "includes/macros.inc.utl"
    macro_file_text = ""

    test_scenarios = [{
        "app": "editorial",
        "site": "http://kearneyhub.com",
        "pkg": "base-kh-oct-2013-1-ads_1.14.2",
        "version": "1.14.2",
        "macros": "includes/macros.inc.utl",
        "type": Package.BLOCK,
        "directory": 'kearneyhub.com/skins/editorial/base-kh-oct-2013-1-ads_1.14.2',
        "expected_macros": set(['archived_asset', 'free_archive_period', 'thisSectionPath',
                                'bloxSelect', 'filterImagesByPresentation',
                                'filterAssetBySubtype', 'filterAssetByPosition',
                                'filterAssetsBySection', 'youtubePlayer',
                                'ifAnonymousUser']),
    }]

    @classmethod
    def setUpTestData(cls):
        """Ensure required model instances are present."""
        # if I make PKG_DIRECTORY absolute, it won't work on other systems. But, if it's
        # relative, it won't work if we're in the wrong directory. So, as a non-solution:
        settings.TNPACKAGE_FILES_ROOT = str(Path('.').resolve() / Path('utl_files/test_data'))

        if not (Path(settings.TNPACKAGE_FILES_ROOT) / cls.PKG_DIRECTORY).is_dir():
            raise Exception("Test data not found. UTLFileTestCase must be run from project root"
                            " directory (location of manage.py).")

        cls.app = Application.objects.get(name='editorial')
        cls.app.save()
        cls.site = TownnewsSite.objects.get(URL='http://richmond.com')
        cls.pkg = Package(name=cls.TEST_PKG,
                          version=cls.TEST_VERSION,
                          is_certified=True,
                          app=cls.app,
                          pkg_type=Package.SKIN,
                          disk_directory=cls.PKG_DIRECTORY)
        cls.pkg.full_clean()
        cls.pkg.save()
        # one of the simplest UTL files in the test data
        cls.simple_utl = UTLFile(file_path=cls.SIMPLE_UTL_FILE, pkg=cls.pkg)
        cls.simple_utl.full_clean()
        cls.simple_utl.save()
        cls.macros_utl = UTLFile(file_path=cls.MACROS_FILE, pkg=cls.pkg)
        cls.macros_utl.full_clean()
        cls.macros_utl.save()
        cls.parse_err_pkg = Package(name='custom-parsing-error',
                                    version='0.1',
                                    is_certified=False,
                                    app=cls.app,
                                    site=cls.site,
                                    last_download="2015-05-01 13:00:00Z",
                                    pkg_type=Package.BLOCK,
                                    disk_directory='omaha.com/blocks/custom-parsing-error')
        cls.parse_err_pkg.full_clean()
        cls.parse_err_pkg.save()

        for scenario in cls.test_scenarios:
            the_app = Application.objects.get(name=scenario["app"])
            the_site = TownnewsSite.objects.get(URL=scenario["site"])
            the_pkg = Package(name=scenario["pkg"],
                              version=scenario["version"],
                              is_certified=False,
                              app=the_app,
                              site=the_site,
                              last_download="2015-05-01 13:00:00Z",
                              pkg_type=scenario["type"],
                              disk_directory=scenario["directory"])
            the_pkg.full_clean()
            the_pkg.save()
            scenario["pkg_id"] = the_pkg.pk
            the_file = UTLFile(pkg=the_pkg,
                               file_path=scenario["macros"])
            the_file.full_clean()
            the_file.save()
            scenario["file_id"] = the_file.pk

    def test_create(self):
        """Unit test for :py:meth:`~utl_files.models.UTLFile`."""
        thefile = UTLFile.objects.get(file_path=self.SIMPLE_UTL_FILE)
        self.assertEqual(thefile.file_path, self.SIMPLE_UTL_FILE)
        self.assertEqual(thefile.pkg, self.pkg)

    def test_base_filename(self):
        """Unit test for :py:meth:`~utl_files.models.UTLFile.base_filename`."""
        thefile = UTLFile.objects.get(file_path=self.SIMPLE_UTL_FILE)
        self.assertEqual(thefile.base_filename, Path(self.SIMPLE_UTL_FILE).name)

    def test_full_file_path(self):
        """:py:meth:`utl_file.models.UTLFile instance has attribute `full_file_path`."""
        self.assertEqual(self.simple_utl.full_file_path, Path(settings.TNPACKAGE_FILES_ROOT) /
                         Path(self.PKG_DIRECTORY) / Path(self.SIMPLE_UTL_FILE))

    def test_to_dict(self):
        """:py:meth:`utl_file.models.UTLFile instance can convert to :py:class:`dict`."""
        expected = {'path': 'includes/footer-spotless.inc.utl',
                    'id': self.simple_utl.id,
                    'pkg_certified': True,
                    'pkg_download': None,
                    'pkg_name': 'skin-editorial-core-base',
                    'pkg_site': None,
                    'pkg_version': '1.45.1.0'}
        actual = self.simple_utl.to_dict()
        self.assertDictEqual(expected, actual)

    def test_str(self):
        """:py:meth:`utl_file.models.UTLFile instance can convert to :py:class:`str`."""
        self.assertEqual(
            str(self.simple_utl), "{}/{}:{}".format(self.TEST_APP, self.TEST_PKG,
                                                    self.SIMPLE_UTL_FILE))

    def test_get_macros_none(self):
        """:py:meth:`utl_file.models.UTLFile.get_macros` can successfully do nothing."""
        self.simple_utl.get_macros()
        self.assertEqual(MacroDefinition.objects.count(), 0)
        self.assertEqual(MacroRef.objects.count(), 0)

    def _verify_macro(self, macro_name, line, start, end):
        """Helper method to compare :py:class:`~utl_files.models.MacroDefinition`
        object to expected values.

        """
        macro_rcd = MacroDefinition.objects.get(name=macro_name)
        self.assertEqual(macro_rcd.source, self.macros_utl)
        self.assertEqual(macro_rcd.line, line)
        self.assertEqual(macro_rcd.start, start)
        self.assertEqual(macro_rcd.end, end)
        if not self.macro_file_text:
            with (Path(settings.TNPACKAGE_FILES_ROOT) / self.PKG_DIRECTORY /
                  self.MACROS_FILE).open('r') as macin:
                self.macro_file_text = macin.read()
        # replicate the processing we did when adding to db
        ws_stripped = re.sub('\\s+\n', '\n', self.macro_file_text[start:end])
        self.assertEqual(macro_rcd.text, ws_stripped)

    def test_get_macros_many(self):
        """:py:meth:`utl_file.models.UTLFile.get_macros` can successfully load macros."""
        self.macros_utl.get_macros()
        self.assertEqual(MacroDefinition.objects.count(), 11)
        self.assertEqual(MacroRef.objects.count(), 14)
        self._verify_macro("archived_asset", 38, 1504, 2069)
        self._verify_macro("free_archive_period", 54, 2071, 2741)
        self._verify_macro("ifAnonymousUser", 356, 12033, 12667)  # last one in file

        for scenario in self.test_scenarios:
            my_source = UTLFile.objects.get(id=scenario["file_id"])
            my_source.get_macros()
            macro_defs = MacroDefinition.objects.filter(source=my_source)
            self.assertSetEqual(set([macro_def.name for macro_def in macro_defs]),
                                scenario["expected_macros"])

    def test_parsing_error(self):
        """Unit test for :py:meth:`utl_file.models.UTLFile.get_macros` parser
        error handling.

        """
        with MockStream().capture_stderr() as fake_stderr:
            for utl_fname in (Path(settings.TNPACKAGE_FILES_ROOT) /
                              Path(self.parse_err_pkg.disk_directory)).glob('**/*.utl'):
                new_file = UTLFile.create_from(utl_fname, self.parse_err_pkg)
                new_file.full_clean()
                new_file.save()
            self.assertIn("ERROR", fake_stderr.logged)
            self.assertIn("block.utl", fake_stderr.logged)
            self.assertIn("Syntax error", fake_stderr.logged)


class PackagePropTestCase(TestCase):
    """Unit tests for :py:class:`uti_files.models.PackageProp`."""

    # pylint:disable=W0201
    @classmethod
    def setUpTestData(cls):
        """Create a package object for tests."""
        cls.test_app = PackageTestCase.find_record_or_create(Application, name='editorial')
        paper = PackageTestCase.find_record_or_create(NewsPaper, name='Richmond Times-Dispatch')
        test_site = PackageTestCase.find_record_or_create(TownnewsSite,
                                                          URL='http://richmond.com',
                                                          name='RTD',
                                                          paper=paper)
        cls.test_pkg = Package(name='some-totally-bogus-pkg',
                               version='1.0',
                               is_certified=True,
                               app=cls.test_app,
                               last_download="2015-05-01 13:00:00Z",
                               disk_directory=("/data/exported/richmond.com/skins/testing/"
                                               "some_totally_bogus_package"),
                               site=test_site,
                               pkg_type=Package.SKIN)
        cls.test_pkg.full_clean()
        cls.test_pkg.save()

        # load files from our test directory, not system directory
        settings.TNPACKAGE_FILES_ROOT = str(Path('.').resolve() / Path('utl_files/test_data'))

    def test_create(self):
        """Unit test for creation of :py:class:`utl_files.models.PackageProp` instance."""
        new_prop = PackageProp(pkg=self.test_pkg, key="fred", value="wilma")
        new_prop.full_clean()
        new_prop.save()
        self.assertEqual(PackageProp.objects.count(), 1)
        test_prop = PackageProp.objects.get(pkg=self.test_pkg, key="fred")
        self.assertEqual(test_prop.pkg, self.test_pkg)
        self.assertEqual(test_prop.key, "fred")
        self.assertEqual(test_prop.value, "wilma")

    def test_unique(self):
        """Unit test to ensure that uniqueness constraint is enforced."""
        new_prop = PackageProp(pkg=self.test_pkg, key="fred", value="wilma")
        new_prop.full_clean()
        new_prop.save()
        new_prop = PackageProp(pkg=self.test_pkg, key="fred", value="betty")
        self.assertRaises(ValidationError, new_prop.full_clean)

    def test_str(self):
        """Unit tests for :py:meth:`utl_files.models.PackageProp.__str__`."""
        new_prop = PackageProp(pkg=self.test_pkg, key="fred", value="wilma")
        self.assertEqual(str(new_prop), 'fred: wilma')

    def test_to_dict(self):
        """Unit tests for :py:meth:`utl_files.models.PackageProp.to_dict`."""
        new_prop = PackageProp(pkg=self.test_pkg, key="fred", value="wilma")
        new_prop.full_clean()
        new_prop.save()
        try:
            self.assertDictContainsSubset({"key": "fred", "value": "wilma", }, new_prop.to_dict())
            self.assertIn("id", new_prop.to_dict())
        finally:
            new_prop.delete()  # clean up for other tests

    def test_from_package_metadata(self):
        """Unit tests for :py:meth:`~utl_files.models.PackageProp.from_package_metadata`.

        """
        antwort_pkg = Package(
            name='custom-newsletter-antwort-columns',
            version='0.15',
            is_certified=False,
            app=Application.objects.get(name='editorial'),
            last_download="2015-05-01 13:00:00Z",
            disk_directory="omaha.com/skins/custom-newsletter-antwort-columns_0.15",
            site=TownnewsSite.objects.get(URL="http://omaha.com"),
            pkg_type=Package.SKIN
        )
        antwort_pkg.full_clean()
        antwort_pkg.save()
        PackageProp.from_package_metadata(antwort_pkg)
        prop_dict = {}
        new_props = PackageProp.objects.filter(pkg=antwort_pkg)
        new_props = PackageProp.objects.filter(pkg=antwort_pkg)
        # 13 keys in file, don't put dependencies in PackageProp
        self.assertEqual(new_props.count(), 12)
        for new_prop in new_props:
            the_prop = new_prop.to_dict()
            prop_dict[the_prop['key']] = the_prop['value']

        self.assertSetEqual(set(prop_dict.keys()),
                            {'description', 'breakpoints', 'app', 'properties',
                             'title', 'blockTypes', 'type', 'capabilities', 'name',
                             'version', 'certified', 'propertyGroups'})


class PackageDepTestCase(TestCase):
    """Unit tests for :py:class:`utl_files.models.PackageDep`."""

    @classmethod
    def setUpTestData(cls):
        """Create required objects"""
        cls.test_app = PackageTestCase.find_record_or_create(Application, name='editorial')
        cls.test_pkg = Package(name='some-totally-bogus-pkg',
                               version='1.0',
                               is_certified=True,
                               app=cls.test_app,
                               last_download="2015-05-01 13:00:00Z",
                               disk_directory=("/data/exported/richmond.com/skins/testing/"
                                               "some_totally_bogus_package"),
                               site=None,
                               pkg_type=Package.SKIN)
        cls.test_pkg.full_clean()
        cls.test_pkg.save()
        cls.test_dep = Package(name='incredibly-important-library',
                               version='3.15',
                               is_certified=True,
                               app=cls.test_app,
                               last_download="2014-02-01 13:00:00Z",
                               disk_directory=("/data/exported/richmond.com/skins/testing/"
                                               "incredibly-important-library"),
                               site=None,
                               pkg_type=Package.SKIN)
        cls.test_dep.full_clean()
        cls.test_dep.save()

    def test_create(self):
        """Unit tests for :py:meth:`utl_files.models.PackageDep`."""
        new_dep = PackageDep(pkg=self.test_pkg,
                             dep_name='incredibly-important-library',
                             dep_pkg=self.test_dep,
                             dep_version='3.15')
        new_dep.full_clean()
        new_dep.save()
        self.assertGreater(PackageDep.objects.count(), 0)
        renew_dep = PackageDep.objects.get(pkg=self.test_pkg, dep_pkg=self.test_dep)
        self.assertIsNotNone(renew_dep)
        self.assertEqual(renew_dep.pkg.id, self.test_pkg.id)
        self.assertEqual(renew_dep.dep_pkg.id, self.test_dep.id)
        self.assertEqual(renew_dep.dep_name, 'incredibly-important-library')
        self.assertEqual(renew_dep.dep_version, '3.15')

    def test_dupes(self):
        """Unit tests for :py:meth:`utl_files.models.PackageDep.full_clean` with duplicate data.

        """
        new_dep = PackageDep(pkg=self.test_pkg,
                             dep_name='incredibly-important-library',
                             dep_pkg=self.test_dep,
                             dep_version='3.15')
        new_dep.full_clean()
        new_dep.save()
        new_dep2 = PackageDep(pkg=self.test_pkg, dep_name='', dep_pkg=self.test_dep, dep_version='')
        self.assertRaises(ValidationError, new_dep2.full_clean)
        new_dep3 = PackageDep(pkg=self.test_pkg,
                              dep_name='incredibly-important-library',
                              dep_pkg=None,
                              dep_version='3.15')
        self.assertRaises(ValidationError, new_dep3.full_clean)

    def test_to_dict(self):
        """Unit tests for :py:meth:`utl_files.models.PackageDep.to_dict`."""
        new_dep = PackageDep(pkg=self.test_pkg,
                             dep_name='incredibly-important-library',
                             dep_pkg=self.test_dep,
                             dep_version='3.15')
        new_dep.full_clean()
        new_dep.save()
        expected = {"pkg_name": self.test_pkg.name,
                    "pkg_version": self.test_pkg.version,
                    "pkg_certified": self.test_pkg.is_certified,
                    "pkg_site": None,
                    "pkg_download": datetime(2015, 5, 1, 13, 0, tzinfo=timezone.utc),
                    "dep_name": self.test_dep.name,
                    "dep_version": self.test_dep.version, }

        actual = new_dep.to_dict()
        self.assertDictContainsSubset(expected, actual)
        self.assertSetEqual(set(['id', ]),
                            set(actual.keys()) - set(expected.keys()))

        self.assertIn("id", new_dep.to_dict())

    def test_str(self):
        """Unit tests for :py:meth:`utl_files.models.PackageDep.__str__`."""
        new_dep = PackageDep(pkg=self.test_pkg,
                             dep_name='incredibly-important-library',
                             dep_pkg=None,
                             dep_version='3.15')
        new_dep.full_clean()
        self.assertEqual(
            str(new_dep), '{}{}::{}/{} depends on {} ({})'.format(
                "certified/" if self.test_pkg.is_certified else "",
                self.test_pkg.app, self.test_pkg.name, self.test_pkg.version,
                new_dep.dep_name, new_dep.dep_version))
        new_dep = PackageDep(pkg=self.test_pkg,
                             dep_name='',
                             dep_pkg=self.test_dep,
                             dep_version='')
        new_dep.full_clean()
        self.assertEqual(
            str(new_dep), '{}{}::{}/{} depends on {} ({})'.format(
                "certified/" if self.test_pkg.is_certified else "",
                self.test_pkg.app, self.test_pkg.name, self.test_pkg.version,
                self.test_dep.name, self.test_dep.version))

    def test_check_for_deps(self):
        """Unit test for :py:meth:`utl_files.models.PackageDep.check_for_deps`."""
        new_dep = PackageDep(pkg=self.test_pkg,
                             dep_name=self.test_dep.name,
                             dep_pkg=None,
                             dep_version=self.test_dep.version)
        new_dep.full_clean()
        new_dep.save()
        self.assertFalse(PackageDep.objects.filter(pkg=self.test_pkg,
                                                   dep_pkg=self.test_dep).exists())
        new_dep.check_for_deps()
        self.assertTrue(PackageDep.objects.filter(pkg=self.test_pkg,
                                                  dep_pkg=self.test_dep).exists())
        # add a dep that doesn't match any  package
        new_dep = PackageDep(pkg=self.test_pkg,
                             dep_name='does-not-exist',
                             dep_pkg=None,
                             dep_version='1.0')
        new_dep.full_clean()
        new_dep.save()
        # all we really require here is that no exception is thrown
        new_dep.check_for_deps()


class MacroDefinitionTestCase(TestCase):
    """Unit tests for :py:class:`utl_files.models.MacroDefinition`."""

    @classmethod
    def setUpTestData(cls):
        """Set up test :model:`utl_files.MacroDefinition` record(s)."""
        cls.app = Application.objects.get(name='editorial')
        cls.app.save()
        cls.pkg = Package(
            name="skin-editorial-core-base",
            version="1.45.1.0",
            is_certified=True,
            app=cls.app,
            pkg_type=Package.SKIN,
            disk_directory='utl_files/test_data/certified/skins/skin-editorial-core-base')
        cls.pkg.full_clean()
        cls.pkg.save()
        cls.utl_file = UTLFile(file_path='includes/header.inc.utl', pkg=cls.pkg)
        cls.utl_file.full_clean()
        cls.utl_file.save()
        cls.test_def = MacroDefinition(source=cls.utl_file,
                                       text='some long text document',
                                       name='my-bogus-macro',
                                       start=0,
                                       end=0,
                                       line=0)
        cls.test_def.full_clean()
        cls.test_def.save()

    def test_str(self):
        """Unit test for :py:meth:`utl_files.models.MacroDefinition.__str__`."""
        self.assertEqual(self.test_def.source.id, self.utl_file.id)
        self.test_def.line = 0
        self.assertEqual(str(self.test_def), 'my-bogus-macro() [0]')
        self.test_def.line = 57
        self.assertEqual(str(self.test_def), 'my-bogus-macro() [57]')

    def test_to_dict(self):
        """Unit test for :py:meth:`utl_files.models.MacroDefinition.to_dict`."""
        self.test_def.line = 57
        expected = {'end': 0,
                    'file': 'includes/header.inc.utl',
                    'line': 57,
                    'name': 'my-bogus-macro',
                    'start': 0,
                    'pkg_name': 'skin-editorial-core-base',
                    'pkg_version': '1.45.1.0',
                    'pkg_certified': True,
                    'pkg_download': None,
                    'pkg_site': None, }
        actual = self.test_def.to_dict()
        self.assertDictContainsSubset(expected, actual)
        # check for unexpected keys
        self.assertSetEqual({'id', },
                            set(actual.keys()) - set(expected.keys()))



class MacroRefTestCase(TestCase):
    """Unit tests for :py:class:`utl_files.models.MacroRef`."""

    @classmethod
    def setUpTestData(cls):
        """Set up required :model:`utl_files.MacroRef` instances."""
        cls.app = Application.objects.get(name='editorial')
        cls.app.save()
        cls.pkg = Package(
            name="skin-editorial-core-base",
            version="1.45.1.0",
            is_certified=True,
            app=cls.app,
            pkg_type=Package.SKIN,
            disk_directory='utl_files/test_data/certified/skins/skin-editorial-core-base')
        cls.pkg.full_clean()
        cls.pkg.save()
        cls.utl_file = UTLFile(file_path='includes/header.inc.utl', pkg=cls.pkg)
        cls.utl_file.full_clean()
        cls.utl_file.save()
        cls.test_ref = MacroRef(source=cls.utl_file,
                                start=2344,
                                line=123,
                                text='my-bogus-macro(bogus1, "some text", 7)',
                                macro_name='my-bogus-macro')
        cls.test_ref.full_clean()
        cls.test_ref.save()

    def test_create(self):
        """Unit test of :py:meth:`utl_files.models.MacroRef`."""
        test_ref = MacroRef.objects.get(source=self.utl_file,
                                        start=2344,
                                        macro_name='my-bogus-macro')
        self.assertEqual(test_ref.line, 123)
        self.assertEqual(test_ref.text, 'my-bogus-macro(bogus1, "some text", 7)')

    def test_str(self):
        """Unit test of :py:meth:`utl_files.models.MacroRef.__str__`."""
        expected = '{}:{} - {}'.format(self.test_ref.line, self.test_ref.start, self.test_ref.text)
        self.assertEqual(str(self.test_ref), expected)

    def test_to_dict(self):
        """Unit test of :py:meth:`utl_files.models.MacroRef.to_dict`."""
        ref = self.test_ref
        pkg = ref.source.pkg
        expected = {"pkg_name": pkg.name,
                    "pkg_version": pkg.version,
                    "file": ref.source.file_path,
                    "line": ref.line,
                    "text": ref.text,
                    "name": ref.macro_name,
                    "pkg_download": pkg.last_download,
                    "pkg_certified": True,
                    "start": ref.start,
                    "pkg_site": pkg.site.URL if pkg.site else None,}

        self.assertDictContainsSubset(expected, self.test_ref.to_dict())
        # make sure id is the only non-checked field in return dictionary
        self.assertSetEqual(set(['id', ]),
                            set(self.test_ref.to_dict().keys()) - set(expected.keys()))
