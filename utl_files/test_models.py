from django.test import TestCase, TransactionTestCase
from django.db.utils import DataError
from django.core.exceptions import ValidationError

from .models import Application, MacroDefinition, MacroRef, Package, PackageDep, PackageProp
from .models import PackageError, UTLFile, UTLFileError


class TestApplication(TestCase):

    def setUp(self):
        """Create a simple Application record for testing."""
        app = Application(name="editorial")
        app.save()

    def test_insert(self):
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


class TestPackage(TransactionTestCase):
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
        self.assertRaises(Package.DoesNotExist, Package.objects.get, name=self.TEST_NAME, version=self.TEST_VERSION)

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
