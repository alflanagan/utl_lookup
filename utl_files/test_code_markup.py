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
        item1 = UTLWithMarkup('[% if fred==wilma then echo "barney"; %]')
        self.assertEqual(item1.source, '[% if fred==wilma then echo "barney"; %]')
        expected = ('[% <span class="statement_list"><span class="if">if '
                    '<span class="expr"><span class="id">fred</span><!-- id '
                    '-->==<span class="id">wilma</span><!-- expr --></span><!-- '
                    'id --> then <span class="statement_list"><span class="echo">'
                    'echo <span class="literal">"barney"</span><!-- if --></span>'
                    '<!-- statement_list --></span><!-- echo --></span><!-- literal'
                    ' -->; %]</span><!-- statement_list -->')
        # TODO: Need a better way to specify expected markup
        self.assertEqual(item1.text, expected)

    def test_document(self):
        """Unit test for :py:meth:`~utl_files.code_markup.UTLWithMarkup.text`
        with only HTML as input.

        """
        item1 = UTLWithMarkup('<div class="fred"><p>a paragraph<p></div>')
        self.assertEqual(item1.source, '<div class="fred"><p>a paragraph<p></div>')

        expected = ('<span class="statement_list"><span class="document">&lt;div '
                    'class=&quot;fred&quot;&gt;&lt;p&gt;a paragraph&lt;p&gt;&lt;'
                    '/div&gt;</span><!-- document --></span><!-- statement_list -->')

        self.assertEqual(item1.text, expected)

    def test_begin_tag(self):
        """Unit tests of """
        source_text = '[% if fred==wilma then echo "barney"; %]'
        item1 = UTLWithMarkup(source_text, markup_start='<start {}>',
                              markup_end='<end {}>')
        # note below how the <end expr> comes before the <end id>, violating
        # the expectation that id will be nested inside the expr. I'm going
        # to wait to see this cause an actual problem before trying to fix it.
        # note 2: is order always same?
        expected = ('[% <start statement_list><start if>if <start expr>'
                    '<start id>fred<end id>==<start id>wilma<end expr><end id>'
                    ' then <start statement_list><start echo>echo '
                    '<start literal>"barney"<end if><end statement_list>'
                    '<end echo><end literal>; %]<end statement_list>')
        self.assertEqual(item1.text, expected)

    def test_comment_markup(self):
        """Test markup for comments in source."""
        source_text = '[% /* this is a comment */ %]<p>fred</p>'
        item1 = UTLWithMarkup(source_text)
        self.assertIn('<span class="comment">/* this is a comment */</span>'
                      '<!-- comment -->',
                      item1.text)
        item2 = UTLWithMarkup(source_text, markup_start='[{}]',
                              markup_end='[{}]')
        self.assertIn('[comment]/* this is a comment */[comment]',
                      item2.text)


if __name__ == '__main__':
    unittest.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
