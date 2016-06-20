#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`code_markup`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods

from django.test import TestCase

from utl_files.code_markup import UTLWithMarkup, UTLTextParseIterator, ParsedSegment


class UTLWithMarkupTestCase(TestCase):
    """Unit tests for class :py:class:`~code_markup.UTLWithMarkup`."""

    def test_create(self):
        """Unit test for :py:meth:`code_markup.UTLWithMarkup`."""
        item1 = UTLWithMarkup('[% if fred==wilma then echo "barney"; %]')
        self.assertEqual(item1.source, '[% if fred==wilma then echo "barney"; %]')
        expected = (r'^\[% <span class="statement_list"><span class="if">if <span class='
                    r'"expr"><span class="id">fred</span><!-- id -->==<span class="id">'
                    r'wilma</span><!-- id --></span><!-- expr --> then (<span class="'
                    r'(statement_list|echo)">){2}echo <span class="literal">&quot;barney'
                    r'&quot;</span><!-- literal -->(</span><!-- (echo|statement_list) -->)'
                    r'{2}</span><!-- if -->; %]</span><!-- statement_list -->$')
        actual = item1.text
        self.assertRegex(actual, expected)

    def test_document(self):
        """Unit test for :py:meth:`~utl_files.code_markup.UTLWithMarkup.text`
        with only HTML as input.

        """
        item1 = UTLWithMarkup('<div class="fred"><p>a paragraph<p></div>')
        self.assertEqual(item1.source, '<div class="fred"><p>a paragraph<p></div>')

        expected = ('<span class="statement_list"><span class="document">&lt;div class=&qu'
                    'ot;fred&quot;&gt;&lt;p&gt;a paragraph&lt;p&gt;&lt;/div&gt;</span><!--'
                    ' document --></span><!-- statement_list -->')

        self.assertEqual(item1.text, expected)

    def test_begin_tag(self):
        """Unit tests of :py:meth:`~utl_files.UTLWithMarkup.text` with a
        non-default start tag template specified.

        """
        source_text = '[% if fred==wilma then echo "barney"; %]'
        item1 = UTLWithMarkup(source_text, markup_start='<start {}>',
                              markup_end='<end {}>')
        # note: order doesn't matter for statement_list and echo after then,
        # because both spans are same length
        expected = (r'^\[% <start statement_list><start if>if <start expr><start id>fred'
                    r'<end id>==<start id>wilma<end id><end expr> then (<start '
                    '(statement_list|echo)>){2}echo <start literal>&quot;barney&quot;<end'
                    ' literal>(<end (echo|statement_list)>){2}<end if>; %]<end '
                    'statement_list>$')
        actual = item1.text
        self.assertRegex(actual, expected)

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

        source_text = ('[% if fred/* Flintstone */==wilma/* wife */ then echo "barney" '
                       '/* friend */; %]')
        item1 = UTLWithMarkup(source_text, markup_end='</span>')
        expected = (r'\[% <span class="statement_list"><span class="if">if <span class='
                    r'"expr"><span class="id">fred</span><span class="comment">/\* '
                    r'Flintstone \*/</span>==<span class="id">wilma</span></span><span class'
                    r'="comment">/\* wife \*/</span> then (<span class="(statement_list|'
                    r'echo)">){2}echo <span class="literal">&quot;barney&quot;(</span>){4}'
                    r' <span class="comment">/\* friend \*/</span>; %]</span>$')

        self.assertRegex(item1.text, expected)


class UTLTextParseIteratorTestCase(TestCase):
    """Unit tests for :py:class:`~utl_lib.code_markup.UTLTextParseIterator`."""

    def test_create(self):
        """Unit test for :py:meth:`code_markup.UTLTextParseIterator`."""
        item1 = UTLTextParseIterator('[% if fred==wilma then echo "barney"; %]')
        self.assertEqual(item1.source, '[% if fred==wilma then echo "barney"; %]')
        self.assertSetEqual(set(item1.start_pos.keys()),
                            set([3, 6, 12, 23, 28]))
        self.assertSetEqual(set(item1.end_pos.keys()),
                            set([10, 17, 36, 40]))
        # should be able to do this with dict comprehension, haven't figured out
        # how **hangs head in shame**
        test_dict = {}
        for key in item1.end_pos:
            test_dict[key] = set([node.symbol for node in item1.end_pos[key]])
        self.assertDictEqual(test_dict,
                             {40: set(['statement_list']),
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
        for parsed_seg in item1.parts:
            self.assertIsInstance(parsed_seg.text, str)
            substrs.append(parsed_seg.text)
            start_nodes.append(set([node.symbol for node in parsed_seg.starts]))
            end_nodes.append(set([node.symbol for node in parsed_seg.ends]))

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
                              {'statement_list'}]  # '; %]'
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
        for segment in item1.parts:
            isinstance(segment, ParsedSegment)
            substrs.append(segment.text)
            start_nodes.append(set([node.symbol for node in segment.starts]))
            end_nodes.append(set([node.symbol for node in segment.ends]))
            is_document.append(segment.is_doc)

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

        expected_end_nodes = [set(),  # '[% '
                              set(),  # 'if '
                              {'id'},  # 'fred'
                              set(),  # '=='
                              {'id', 'expr'},  # 'wilma'
                              set(),  # ' %] '
                              {'statement_list'},  # '<p>first para<p> '
                              set(),  # '[% '
                              set(),  # 'else %] '
                              {'statement_list', 'else'},  # '<span> second doc </span> '
                              {'if'},  # '[% end'
                              {'statement_list'}]  # '; %]'
        self.assertSequenceEqual(expected_end_nodes, end_nodes)

        expected_docs = [False, False, False, False, False, False, True,
                         False, False, True, False, False]
        self.assertSequenceEqual(expected_docs, is_document)

    def test_missing_close_bracket(self):
        """Test expected output from
        :py:meth:`~utl_files.code_markup.UTLTextParseIterator.parts` when
        source text lacks a closing '%]'.

        """
        item1 = UTLTextParseIterator('if a then b end')
        parts = list(item1.parts)
        self.assertEqual(len(parts), 1)
        self.assertTrue(parts[0].is_doc)  # document
        item1 = UTLTextParseIterator('[% if a then b%]')
        parts = list(item1.parts)
        self.assertEqual(len(parts), 6)
        self.assertSequenceEqual([part.text for part in parts],
                                 ['[% ', 'if ', 'a', ' then ', 'b', '%]'])
        self.assertSequenceEqual([set([node.symbol for node in part.starts]) for part in parts],
                                 [set(), {'statement_list', 'if'}, {'id'}, set(),
                                  {'statement_list', 'id'}, set()])
        self.assertSequenceEqual([set([node.symbol for node in part.ends]) for part in parts],
                                 [set(), set(), {'id'}, set(),
                                  {'statement_list', 'id', 'if'}, {'statement_list'}])
        self.assertSequenceEqual([part.is_doc for part in parts], [False] * 6)


# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
