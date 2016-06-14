#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`code_markup`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods

import unittest

from utl_files.code_markup import UTLWithMarkup, UTLTextParseIterator


class UTLWithMarkupTestCase(unittest.TestCase):
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


class UTLTextParseIteratorTestCase(unittest.TestCase):
    """Unit tests for :py:class:`~utl_lib.code_markup.UTLTextParseIterator`."""

    def test_create(self):
        """Unit test for :py:meth:`code_markup.UTLTextParseIterator`."""
        item1 = UTLTextParseIterator('[% if fred==wilma then echo "barney"; %]')
        self.assertEqual(item1.source, '[% if fred==wilma then echo "barney"; %]')
        self.assertSetEqual(set(item1.start_pos.keys()),
                            set([3, 6, 12, 23, 28]))
        self.assertSetEqual(set(item1.end_pos.keys()),
                            set([10, 17, 36, 41]))
        # should be able to do this with dict comprehension, haven't figured out
        # how **hangs head in shame**
        test_dict = {}
        for key in item1.end_pos:
            test_dict[key] = set([node.symbol for node in item1.end_pos[key]])
        self.assertDictEqual(test_dict,
                             {41: set(['statement_list']),
                              10: set(['id']),
                              36: set(['if', 'statement_list', 'echo', 'literal']),
                              17: set(['expr', 'id'])})

        test_dict = {}
        for key in item1.start_pos:
            test_dict[key] = set([node.symbol for node in item1.start_pos[key]])
        self.assertDictEqual(test_dict,
                             {28: set(['literal']),
                              3: set(['statement_list', 'if']),
                              12: set(['id']),
                              6: set(['expr', 'id']),
                              23: set(['statement_list', 'echo'])})

    def test_iterate(self):
        """Unit test for :py:meth:`code_markup.UTLTextParseIterator`."""
        # added single-letter ID to catch edge cases :)
        item1 = UTLTextParseIterator('[% if fred==wilma then echo i + "barney"; %]')

        substrs = []
        start_nodes = []
        end_nodes = []
        for part in item1.parts:
            self.assertIsInstance(part[0], str)
            substrs.append(part[0])
            start_nodes.append(set([node.symbol for node in part[1]]))
            end_nodes.append(set([node.symbol for node in part[2]]))

        expected_strs = ['[% ', 'if ', 'fred', '==', 'wilma', ' then ',
                         'echo ', 'i', ' + ', '"barney"', '; %]']
        self.assertSequenceEqual(expected_strs, substrs)

        expected_start_nodes = [set(),  # '[% '
                                {'if', 'statement_list'},  # 'if '
                                {'expr', 'id'},  # 'fred'
                                set(),  # '=='
                                {'id'},  # 'wilma'
                                set(),  # ' then '
                                {'echo', 'statement_list'},  # 'echo '
                                {'expr', 'id'},  # 'i'
                                set(),  # ' + '
                                {'literal'},  # '"barney"'
                                set()]  # '; %]'
        self.assertSequenceEqual(expected_start_nodes, start_nodes)

        # so start nodes are nodes that start immediately before substr, end
        # nodes are nodes that end immediately after substr. so if substr
        # matches a production by itself the node will appear in both sets
        expected_end_nodes = [set(),  # '[% '
                              set(),  # 'if '
                              {'id'},  # 'fred'
                              set(),  # '=='
                              {'id', 'expr'},  # 'wilma'
                              set(),  # ' then '
                              set(),  # 'echo '
                              {'id'},  # 'i'
                              set(),  # ' + '
                              {'literal', 'echo', 'statement_list', 'if', 'expr'},  # '"barney"'
                              set()]  # '; %]'
        self.assertSequenceEqual(expected_end_nodes, end_nodes)

    def test_w_docs(self):
        """Unit test for :py:meth:`code_markup.UTLTextParseIterator`."""
        # added single-letter ID to catch edge cases :)
        item1 = UTLTextParseIterator('[% if fred==wilma %] <p>first para<p> [% else %] <span>'
                                     ' second doc </span> [% end %]')

        substrs = []
        start_nodes = []
        end_nodes = []
        is_document = []
        for part in item1.parts:
            substrs.append(part[0])
            start_nodes.append(set([node.symbol for node in part[1]]))
            end_nodes.append(set([node.symbol for node in part[2]]))
            is_document.append(part[3])

        # note problem with our parser: it doesn't break out keywords from  %], [%
        expected = ['[% ', 'if ', 'fred', '==', 'wilma', ' %] ', '<p>first para<p> ', '[% ',
                    'else %] ', '<span> second doc </span> ', '[% end', ' %]']
        self.assertSequenceEqual(expected, substrs)

        expected_docs = [False, False, False, False, False, False, True, False,
                         False, True, False, False]
        self.assertSequenceEqual(expected_docs, is_document)

        expected_start_nodes = [set(),  # '[% '
                                {'if', 'statement_list'},  # 'if '
                                {'expr', 'id'},  # 'fred'
                                set(),  # '=='
                                {'id'},  # 'wilma'
                                set(),  # ' %] '
                                {'statement_list'},  # '<p>first para<p> '
                                set(),  # '[% '
                                {'else'},  # 'else %] '
                                {'statement_list'},  # '<span> second doc </span> '
                                set(),  # '[% end'
                                set()]  # '; %]'
        self.assertSequenceEqual(expected_start_nodes, start_nodes)

        # TODO: update this for this test!!
        expected_end_nodes = [set(),  # '[% '
                              set(),  # 'if '
                              {'id'},  # 'fred'
                              set(),  # '=='
                              {'id', 'expr'},  # 'wilma'
                              set(),  # ' then '
                              set(),  # 'echo '
                              {'id'},  # 'i'
                              set(),  # ' + '
                              {'literal', 'echo', 'statement_list', 'if', 'expr'},  # '"barney"'
                              set()]  # '; %]'
        self.assertSequenceEqual(expected_end_nodes, end_nodes)


if __name__ == '__main__':
    unittest.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
