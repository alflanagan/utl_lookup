#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module of classes/functions to aid in testing.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from unittest.util import safe_repr
from datetime import timedelta
from pathlib import Path
from html.parser import HTMLParser


class SimpleImgTag(HTMLParser):
    """A parser that, given an <img> tag, will create a dictionary of the tag's attributes.

    :Parameter:

        `tag_text`: A string containing a valid <img> tag.

    >>> a = SimpleImgTag('<img src="http://www.example.com/frankenstein.jpg">')
    >>> a.attrs
    {'src': 'http://www.example.com/frankenstein.jpg'}

    """
    def __init__(self, tag_text):
        HTMLParser.__init__(self, convert_charrefs=True)
        # strip out anything except <img> tag. we hope.
        tag_pos = tag_text.find('<img')
        if tag_pos < 0:
            raise ValueError("No <img> tag found in data: '{0}'".format(tag_text))
        tag_end = tag_text.rfind('>')
        if tag_end < 0:
            raise ValueError("Incomplete <img> tag in data: '{0}'".format(tag_text))
        if tag_pos:
            tag_text = tag_text[tag_pos:tag_end + 1]
        self._attrs = []
        self.feed(tag_text)
        self.close()

    def handle_starttag(self, tag_name, attrs):
        """Override :py:meth:`html.parser.HTMLParser.handle_starttag` to store attribute list."""
        assert tag_name == 'img'  # should be guaranteed by __init__()
        self._attrs = attrs

    @property
    def attrs(self):
        """a dictionary of the <img> tag's attributes."""
        assert isinstance(self._attrs, list)
        return dict(self._attrs)

    def error(self, message):
        raise Exception(message)


# pylint: disable=C0103
class TestCaseMixin(object):
    """Even with all the `assertXxxx()` methods provided by :py:class:`unittest.TestCase`, I
    found I wanted more. This class provides them without inheriting from
    :py:class:`unittest.TestCase`, thus avoiding possible multiple-inheritance issues with, for
    example, Django's classes which derive from that class.

    Note: this class is following :py:class:`unittest.TestCase` method-naming convention, which
    follows java's conventions, not python's.

    """
    def assertSubset(self, small_set, big_set, msg=None):
        """:param set small_set: a :py:class:`set` expected to be a subset of `big_set`

        :param set big_set: a :py:class:`set` expected to be a superset of `small_set`

        :param str msg: a customized error message. If ommitted, uses the message produced by
            :py:meth:`unittest.TestCase.assertIn`

        :raises `AssertionError`: unless every item of `small_set` is found in `big_set`.

        """
        # TODO: Collect missing items, better error message
        for item in small_set:
            self.assertIn(item, big_set, msg)

    def assertInRange(self, value, low, high, msg='{0} not in range {1} - {2}'):
        """Asserts that `value` is in the range `low` – `high`.

        :param value: the unknown value
        :param low: the minimum of the asserted range
        :param high: the maximum of the asserted range

        All three parameters must be mutually orderable, i.e. ``<=`` is valid for comparisons.

        :raises AssertionError: unless ``low <= value <= high``.

        """
        self.assertGreater(high, low, "assertInRange() called with low >= high value.")
        formatted = msg.format(str(value), str(low), str(high))
        self.assertLessEqual(value, high, formatted)
        self.assertGreaterEqual(value, low, formatted)

    # pylint: disable=W0702
    def assertDoesNotRaise(self, exc_class, callable_obj, *args, **kwargs):
        """Calls :py:func:`callable_obj` with arguments `args` and keyword arguments `kwargs`.

        :param type exc_class: An exception type
        :param callable callable_obj: A callable object
        :param args: arguments
        :param kwargs: keyword arguments

        :raises AssertionError: if the call of :py:func:`callable_obj` raises an exception of
            type `exc_class`. *Succeeds if :py:func:`callable_obj` raises an exception of some
            other type.*

        """
        try:
            callable_obj(*args, **kwargs)
        except exc_class:
            self.fail("callable {0} raised exception {1}"
                      "".format(str(callable_obj), exc_class.__name__))
        except:  # it's OK to raise other exceptions
            pass

    def assertHasAttr(self, an_obj, attr_name, msg="Object {0} missing required attribute {1}"):
        """Tests whether `an_obj` has the specified attribute.

        :param object an_obj: an object with attributes.

        :param str attr_name: the name of an expected attribute.

        :param str msg: an error message to be displayed. If ``'{0}'`` and ``'{1}'`` are
            present in the string, they will be replaced with the values of ``str(an_obj)``
            and `attr_name`, respectively.

        :raises AssertionError: if `an_obj` does not have an attribute named `attr_name`.

        """
        if not hasattr(an_obj, attr_name):
            self.fail(msg.format(str(an_obj), attr_name))

    def assertImgTagsEqual(self, img_tag1, img_tag2,
                           msg="Two <img> tags are not equivalent: '{0}' and '{1}'."):
        """Succeeds if two <img> tags are functionally equivalent, i.e. have same attributes
        and values, regardless of order.

        :param str img_tag1: An <img> tag

        :param str img_tag2: Another <img> tag

        :param str msg: An error message to be used if the tags are not equal. If strings '{0}' and
            '{1}' are present in `msg`, they will be replaced with the values of `img_tag1` and
            `img_tag2`, respectively.

        :raises AssertionError: if either parameter is not of type `str`
        :raises AssertionError: if the tags do not have same attribute values and keys.

        """
        self.assertIsInstance(img_tag1, str)
        self.assertIsInstance(img_tag2, str)
        attrs1 = SimpleImgTag(img_tag1).attrs
        attrs2 = SimpleImgTag(img_tag2).attrs
        if "{1}" in msg:
            self.assertDictEqual(attrs1, attrs2, msg.format(img_tag1, img_tag2))
        else:
            self.assertDictEqual(attrs1, attrs2, msg)

    def assertDictContainsSubset(self, dictionary, subset, msg=None):
        """Checks whether dictionary is a superset of subset.

        :param dict dictionary: the :py:class:`dict` to be tested.

        :param dict subset: :py:class:`dict` expected be a subset of `dictionary`.

        :param str msg: Customized message for the :py:class:`AssertionError` raised if test
            fails.

        :raises AssertionError: if any key in `subset` is not in `dictionary`

        :raises AssertionError: if a key is in `subset`, but ``subset[key] != dictionary[key]``.

        The default error message will include a line listing all the keys in `subset` which
        are not present in `dictionary`, and a line listing the actual and expected values for
        each key where the value differs between the two.

        Replacement for standard library version, which is deprecated for no obvious reason.

        """
        # and this is the code from the unittest.TestCase class, with DeprecationWarning
        # removed (but fixed questionable parameter order)
        missing = []
        mismatched = []
        for key, value in subset.items():
            if key not in dictionary:
                missing.append(key)
            elif value != dictionary[key]:
                mismatched.append('%s, expected: %s, actual: %s' %
                                  (safe_repr(key), safe_repr(value),
                                   safe_repr(dictionary[key])))

        if not (missing or mismatched):
            return

        standardMsg = ''
        if missing:
            standardMsg = 'Missing key: %s' % ','.join(safe_repr(m) for m in
                                                       missing)
        if mismatched:
            if standardMsg:
                standardMsg += '; '
            standardMsg += 'Mismatched values: %s' % ','.join(mismatched)

        self.fail(self._formatMessage(msg, standardMsg))

    def assertDatesAreClose(self, date1, date2, seconds_tolerance=1,
                            msg="Dates differ by more than {0} seconds: {1} - {2}."):
        """Asserts that two :py:class:`datetime` instances differ by no more than
        ``seconds_tolerance`` seconds.

            :param datetime date1: The first date (order of dates not important).

            :param datetime date2: A second date.

            :param float seconds_tolerance: The maximum interval in seconds between ``date1``
                and ``date2``.

                :note: ``seconds_tolerance`` should be positive and is compared to the absolute
                    value of the difference.

            :param str msg: Customized message for the :py:class:`AssertionError` raised if test
                fails.

            :raises AssertionError: If the interval between ``date1`` and ``date2`` exceeds
                ``seconds_interval``.

            :raises TypeError: If the difference between ``date1`` and ``date2`` is not a
                :py:class:`datetime.timedelta` instance. (Currently, this means they must both
                be of type :py:class:`datetime.date`, or both be of type
                :py:class:`datetime.datetime`).

            The default error message will report the maximum tolerance given, and the actual
            values of the two dates.

            """
        tolerance = timedelta(0, seconds_tolerance, 0)
        diff = abs(date1 - date2)
        # assertLessEqual doesn't allow override of standard message, it just adds to it.
        # self.assertLessEqual(diff, tolerance,
        #                      msg.format(seconds_tolerance, date1, date2))
        if diff > tolerance:
            self.fail(msg.format(safe_repr(seconds_tolerance), safe_repr(date1),
                                 safe_repr(date2)))

    # pylint: disable=too-many-arguments
    def assertAttribValue(self, some_obj, dict_name, key, value, msg=None):
        """
        Asserts that ``some_obj.dict_name[key] == value``. With better failure messages.

        """
        the_dict = getattr(some_obj, dict_name)
        self.assertIsNotNone(the_dict, msg=msg)
        self.assertIn(key, the_dict,
                      msg or "{} object missing expected attribute: {}.{}.".format(
                          some_obj.__class__.__name__, dict_name, safe_repr(key)))
        self.assertEqual(the_dict[key], value,
                         msg or "{} object expected {}[{}] to have value {}, got {} instead."
                         "".format(some_obj.__class__.__name__, dict_name, safe_repr(key),
                                   safe_repr(value), safe_repr(the_dict[key])))

    def assertFSNotExists(self, pathname,
                          msg="File sytem path '{}' exists."):
        """
        Asserts that a file system object named `pathname` does not exist.

        """
        if Path(pathname).exists():
            self.fail(msg.format(pathname))

    def assertFSExists(self, pathname,
                       msg="File sytem path '{}' does not exist."):
        """
        Asserts that a file system object named `pathname` exists.

        """
        if not Path(pathname).exists():
            self.fail(msg.format(pathname))

    def assertFSAllExist(self, *args, msg=None):
        """
        Asserts that all file system objects named as an argument do not exist.

        """
        bad_paths = []
        for arg in args:
            if not Path(arg).exists():
                bad_paths.append(str(arg))
        if bad_paths:
            if msg is not None:
                self.fail(msg.format(", ".join(bad_paths)))
            else:
                if len(bad_paths) > 1:
                    self.fail("File system paths [{}] do not exist.".format(", ".join(bad_paths)))
                else:
                    self.fail("File system path '{}' does not exist.".format(bad_paths[0]))

    def assertFSNoneExist(self, *args, msg=None):
        """
        Asserts that none of the file system objects named as an argument exist.

        """
        bad_paths = []
        for arg in args:
            if Path(arg).exists():
                bad_paths.append(str(arg))
        if bad_paths:
            if msg is not None:
                self.fail(msg.format(", ".join(bad_paths)))
            elif len(bad_paths) > 1:
                self.fail("File system paths [{}] exist.".format(", ".join(bad_paths)))
            else:
                self.fail("File system path '{}' exists.".format(bad_paths[0]))


# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
