#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`code_markup`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods

# this script doesn't require Django database support
import sys
from unittest import TestCase, main

from utl_files.code_markup import UTLWithMarkup, UTLTextParseIterator, ParsedSegment
from utl_lib.ast_node import ASTNode


class UTLWithMarkupTestCase(TestCase):
    """Unit tests for class :py:class:`~code_markup.UTLWithMarkup`."""

    def test_create(self):
        """Unit test for :py:meth:`code_markup.UTLWithMarkup`."""
        item1 = UTLWithMarkup('[% if fred==wilma then echo "barney"; %]')
        self.assertEqual(item1.source, '[% if fred==wilma then echo "barney"; %]')
        expected = (r'^\[% (<span class="(statement_list|utldoc|abbrev_if_stmt|statement)">){4}if '
                    r'(<span class="(expr|id)">){3}fred(</span><!-- (id|expr) -->){2}==(<span '
                    r'class="(id|expr)">){2}wilma(</span><!-- (id|expr) -->){3} then (<span '
                    r'class="(echo|statement)">){2}echo (<span class="(literal|expr)">){2}&quot;'
                    r'barney&quot;(</span><!-- (expr|literal|echo) -->){3}'
                    r'<span class="eostmt">;(</span><!-- (eostmt|statement|abbrev_if_stmt) -->){4}'
                    r' (<span class="(statement|eostmt)">){2}%](</span><!-- (eostmt|'
                    r'statement|statement_list|utldoc) -->){4}$')
        actual = item1.text
        self.assertRegex(actual, expected)

    def test_document(self):
        """Unit test for :py:meth:`~utl_files.code_markup.UTLWithMarkup.text`
        with only HTML as input.

        """
        item1 = UTLWithMarkup('<div class="fred"><p>a paragraph<p></div>')
        self.assertEqual(item1.source, '<div class="fred"><p>a paragraph<p></div>')

        expected = (r'(<span class="(statement_list|document|utldoc|statement)">){4}&lt;div '
                    r'class=&quot;fred&quot;&gt;&lt;p&gt;a paragraph&lt;p&gt;&lt;/div&gt;(</span>'
                    r'<!-- (document|statement|statement_list|utldoc) -->){4}$')
        actual = item1.text
        self.assertRegex(actual, expected)

    def test_begin_tag(self):
        """Unit tests of :py:meth:`~utl_files.UTLWithMarkup.text` with a
        non-default start tag template specified.

        """
        source_text = '[% if fred==wilma then echo "barney"; %]'
        item1 = UTLWithMarkup(source_text, markup_start='<start {}>',
                              markup_end='<end {}>')
        expected = (r'^\[% (<start (statement_list|abbrev_if_stmt|statement|utldoc)>){4}'
                    r'if (<start (expr|id)>){3}fred(<end (id|expr)>){2}==(<start (expr|id)>){2}'
                    r'wilma(<end (expr|id)>){3} then (<start (statement|echo)>){2}'
                    r'echo (<start (literal|expr)>){2}&quot;barney&quot;'
                    r'(<end (literal|expr|echo)>){3}'
                    r'<start eostmt>;(<end (eostmt|statement|abbrev_if_stmt)>){4}'
                    r' (<start (eostmt|statement)>){2}%]'
                    r'(<end (eostmt|statement|utldoc|statement_list)>){4}$')
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
        expected = (r'^\[% (<span class="(statement_list|utldoc|statement|abbrev_if_stmt)">){4}if '
                    r'(<span class="(expr|id)">){3}fred(</span>){2}<span class="comment">/\* '
                    r'Flintstone \*/</span>==(<span class="(id|expr)">){2}wilma(</span>){3}'
                    r'<span class="comment">/\* wife \*/</span> then (<span class="(statement|'
                    r'echo)">){2}echo (<span class="(literal|expr)">){2}&quot;barney&quot;(</span>)'
                    r'{3} <span class="comment">/\* friend \*/</span><span class="eostmt">;'
                    r'(</span>){4} (<span class="(eostmt|statement)">){2}%](</span>){4}$')
        actual = item1.text
        self.assertRegex(actual, expected)

    def test_markup_start(self):
        """Unit tests for :py:meth:`~utl_files.code_markup.UTLWithMarkup.markup_start`."""
        fred = UTLWithMarkup('')
        self.assertEqual(fred.markup_start('test'), '<span class="test">')

        wilma = UTLWithMarkup('', markup_start='hello, {}')
        self.assertEqual(wilma.markup_start('test'), 'hello, test')

        the_node = ASTNode('goodbye', {}, [])
        self.assertEqual(fred.markup_start(the_node), '<span class="goodbye">')
        self.assertEqual(wilma.markup_start(the_node), 'hello, goodbye')

    def test_markup_end(self):
        """Unit tests for :py:meth:`~utl_files.code_markup.UTLWithMarkup.markup_end`."""
        fred = UTLWithMarkup('')
        self.assertEqual(fred.markup_end('test'), '</span><!-- test -->')

        wilma = UTLWithMarkup('', markup_end='hello, {}')
        self.assertEqual(wilma.markup_end('test'), 'hello, test')

        the_node = ASTNode('goodbye', {}, [])
        self.assertEqual(fred.markup_end(the_node), '</span><!-- goodbye -->')
        self.assertEqual(wilma.markup_end(the_node), 'hello, goodbye')


class UTLTextParseIteratorTestCase(TestCase):
    """Unit tests for :py:class:`~utl_lib.code_markup.UTLTextParseIterator`."""

    def test_create(self):
        """Unit test for :py:meth:`code_markup.UTLTextParseIterator`."""
        item1 = UTLTextParseIterator('[% if fred==wilma then echo "barney"; %]   ')
        self.assertEqual(item1.source, '[% if fred==wilma then echo "barney"; %]   ')

        expected_starts = {3: {"utldoc", "statement_list", "statement", "abbrev_if_stmt"},
                           6: {"expr", "expr", "id"},
                           12: {"expr", "id"},
                           23: {"statement", "echo"},
                           28: {"expr", "literal"},
                           36: {"eostmt"},
                           38: {"statement", "eostmt"}}
        self.assertEqual(item1.start_pos.keys(), expected_starts.keys())
        for key in expected_starts:
            self.assertSetEqual(set([node.symbol for node in item1.start_pos[key]]),
                                expected_starts[key])
        expected_ends = {10: {'expr', 'id'},
                         17: {'expr', 'expr', 'id'},
                         36: {'echo', 'expr', 'literal'},
                         37: {'statement', 'abbrev_if_stmt', 'statement', 'eostmt'},
                         40: {'statement', 'eostmt'},
                         43: {'utldoc', 'statement_list'}}

        self.assertEqual(expected_ends.keys(), item1.end_pos.keys())
        for key in expected_ends:
            self.assertSetEqual(set([node.symbol for node in item1.end_pos[key]]),
                                expected_ends[key])

    def test_iterate(self):
        """Unit test for :py:meth:`code_markup.UTLTextParseIterator`."""
        # TODO: need to incorporate case from parts where anchor not set to end
        # may have to mangle data to trigger that case.
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
                         'echo ', 'i', ' + ', '"barney"', ';', ' ', '%]']
        self.assertSequenceEqual(expected_strs, substrs)

        expected_start_nodes = [set(),  # '[% '
                                {'abbrev_if_stmt', 'statement_list', 'statement',
                                 'utldoc'},  # 'if '
                                {'expr', 'id'},  # 'fred'
                                set(),  # '=='
                                {'expr', 'id'},  # 'wilma'
                                set(),  # ' then '
                                {'echo', 'statement'},  # 'echo '
                                {'expr', 'id'},  # 'i'
                                set(),  # ' + '
                                {'literal', 'expr'},  # '"barney"'
                                {'eostmt'},  # '; '
                                set(),  # ' '
                                {'statement', 'eostmt'}]  # '%]'
        self.assertSequenceEqual(expected_start_nodes, start_nodes)

        # so start nodes are nodes that start immediately before substr, end
        # nodes are nodes that end immediately after substr. so if substr
        # matches a production by itself the node will appear in both sets

        expected_end_nodes = [set(),  # '[% '
                              set(),  # 'if '
                              {'expr', 'id'},  # 'fred'
                              set(),  # '=='
                              {'id', 'expr'},  # 'wilma'
                              set(),  # ' then '
                              set(),  # 'echo '
                              {'id', 'expr'},  # 'i'
                              set(),  # ' + '
                              {'literal', 'echo', 'expr'},  # '"barney"'
                              {'abbrev_if_stmt', 'statement', 'eostmt'},  # ';'
                              set(),  # ' '
                              {'statement', 'statement_list', 'utldoc', 'eostmt'}]  # '%]'
        self.assertSequenceEqual(expected_end_nodes, end_nodes)

    def test_w_docs(self):
        """Unit test for :py:meth:`code_markup.UTLTextParseIterator`."""
        item1 = UTLTextParseIterator('[% if fred==wilma %] <p>first para<p> [% else %] <span>'
                                     ' second doc </span> [% end %]')

        expected = [('[% ', False, set(), set()),
                    ('if ', False, {"utldoc", "statement_list", "statement", "if_stmt"}, set()),
                    ('fred', False, {"expr", "id", "expr"}, {"id", "expr"}),
                    ('==', False, set(), set()),
                    ('wilma', False, {"expr", "id"}, {"expr", "id", "expr"}),
                    (' ', False, set(), set()),
                    ('%]', False, {"eostmt"}, {"eostmt"}),
                    (' ', False, set(), set()),
                    ('<p>first para<p> ', True, {"statement_list", "statement"},
                     {"statement_list", "statement"}),
                    ('[% ', False, set(), set()),
                    ('else ', False, {"else_stmt"}, set()),
                    ('%]', False, {"eostmt"}, {"eostmt"}),
                    (' ', False, set(), set()),
                    ('<span> second doc </span> ', True, {"statement", "statement_list"},
                     {"statement", "statement_list", "else_stmt"}),
                    ('[% end', False, set(), {"if_stmt"}),
                    (' ', False, set(), set()),
                    ('%]', False, {"eostmt"}, {"eostmt", "statement", "utldoc", "statement_list"})]

        actual = [(part.text,
                   part.is_doc,
                   set([start.symbol for start in part.starts]),
                   set([end.symbol for end in part.ends]), )
                  for part in item1.parts]
        self.assertSequenceEqual(actual,
                                 expected)

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
                                 [set(),
                                  {'statement_list', 'utldoc', 'abbrev_if_stmt', 'statement'},
                                  {'id', 'expr'},
                                  set(),
                                  {'statement', 'id', 'expr'},
                                  {'eostmt'}])
        self.assertSequenceEqual([set([node.symbol for node in part.ends]) for part in parts],
                                 [set(),
                                  set(),
                                  {'id', 'expr'},
                                  set(),
                                  {'id', 'expr'},
                                  {'statement_list', 'eostmt', 'utldoc', 'statement',
                                   'abbrev_if_stmt'}])
        self.assertSequenceEqual([part.is_doc for part in parts], [False] * 6)

    def test_markup_whitespace(self):
        test_doc = ('[% macro core_site_insert_classifiedsSearchTopFull;\n'
                    '    /* real estate top tabs */\n'
                    '    core_site_realestate_TopTabs;\n'
                    'end; %]\n')
        item1 = UTLTextParseIterator(test_doc)
        parts = list(item1.parts)
        self.assertEqual(len(parts), 13)
        self.assertEqual(''.join([part.text for part in parts]), test_doc)
        for part in parts:
            isinstance(part, ParsedSegment)
            part_str = "|".join([start.symbol for start in part.starts])
            part_str += ": {} :".format(part.text)
            part_str += "|".join([end.symbol for end in part.ends])
            print(part_str)


if __name__ == '__main__':
    # this is useful for running these tests without creating a test database,
    # which we don't use in this file.
    main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
