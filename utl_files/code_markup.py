#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module to provide syntax markup for UTL code.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""


import html
from collections import defaultdict
from typing import Union, Sequence, Iterator

from utl_lib.ast_node import ASTNode, FrozenASTNode
from utl_lib.handler_parse_tree import UTLParseHandlerParseTree
from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_lex_comments import UTLLexerComments

# pylint: disable=too-few-public-methods


class ParsedSegment(object):
    """A not-smart holder for info about a piece of UTL source code which
    will not require further splitting for syntax markup.

    """
    @staticmethod
    def _ast_node_sort_key(a_node):
        """Return length of source string to define a sorting key."""
        try:
            return a_node.attributes["end"] - a_node.attributes["start"]
        except KeyError:
            return 0

    def __init__(self, text: str, starts: Sequence[ASTNode],
                 ends: Sequence[ASTNode], is_document: bool):
        self.text = text
        self.starts = list(starts)
        self.ends = list(ends)
        self.is_doc = is_document

        # For retrieval of starts, we want the outer nodes first
        # For retrieval of ends, we want the inner nodes first
        # so we need to sort by size
        self.starts.sort(key=self._ast_node_sort_key, reverse=True)
        self.ends.sort(key=self._ast_node_sort_key)


class UTLTextParseIterator():
    """A data structure to hold information needed to process a UTL text
    source into marked-up output. This is a sufficently hard problem to
    deserve its own class (implementated as a source code iterator).

    The fundamental problem is this: the parser operates on the raw source
    code (naturally). To do markup and display, we need to html-escape the
    source code, which changes its length. This causes the text to no longer
    match the start and end positions in the parse tree. So we need to set up
    the parse info and source in such a way that the source can be
    html-escaped without breaking the parse data.

    The iterator will successively return each substring of the source code
    which is the longest subinterval which does not require insertion of
    markup into the text, along with all the information needed to add
    whatever markup we desire.

    :param str source_text: Valid UTF source code.

    """

    def __init__(self, source_text):
        self.parser = UTLParser([UTLParseHandlerParseTree(exception_on_error=True)])
        self.source = source_text
        self.parse_tree = self.parser.parse(self.source)
        self.parse_tree = FrozenASTNode(self.parse_tree)
        self.start_pos = defaultdict(list)
        """Mapping from source text position to the production node(s) that
        start there.

        """
        self.end_pos = defaultdict(list)
        """Mapping from source text position to the production node(s) that
        end there.

        """
        self.documents = {}
        """Mapping from source text position to the text of a document that
        starts there.

        """
        self._find_boundaries()

    def _find_boundaries(self):
        """Creates dictionaries to map source text character positions to the
        productions that start or end there, or to the text of documents that
        start there.

        """
        limit = len(self.source)
        for ast_node in self.parse_tree.walk():
            if ast_node.symbol == 'document':
                self.documents[ast_node.attributes["start"]] = ast_node.attributes["text"]
            else:
                # omit productions that didn't match any text
                if ("start" in ast_node.attributes and
                        "end" in ast_node.attributes and
                        ast_node.attributes["start"] != ast_node.attributes["end"]):
                    self.start_pos[ast_node.attributes["start"]].append(ast_node)
                    # parser may report end one past len(source), but we
                    # don't need to check that far
                    end_position = min(ast_node.attributes["end"], limit)
                    self.end_pos[end_position].append(ast_node)

        for comm_start, comm_end in self._get_comments():
            comment_node = FrozenASTNode(ASTNode("comment", {}, []))
            self.start_pos[comm_start].append(comment_node)
            self.end_pos[comm_end].append(comment_node)

        # basic sanity check: # starts == # ends
        start_ct = sum([len(self.start_pos[key]) for key in self.start_pos])
        end_ct = sum([len(self.end_pos[key]) for key in self.end_pos])
        assert start_ct == end_ct

    def _get_comments(self) -> Sequence[tuple]:
        """Use :py:class:`utl_files.UTLLexerComments` to find comments.

        :returns set: Set of tuples of int (start, end) defining characters between start and end as
            part of a comment in `self.source`.

        """
        spans = []
        lexer = UTLLexerComments()
        lexer.input(self.source)
        next_tok = lexer.token()
        while next_tok:
            if next_tok.type == 'COMMENT':
                spans.append((next_tok.lexpos, next_tok.lexpos + len(next_tok.value), ))
            next_tok = lexer.token()
        return tuple(spans)

    @property
    def parts(self) -> Iterator[ParsedSegment]:
        """Returns an iterator which returns a
        :py:class:`~utl_files.code_markup.ParsedSegment` for each substring
        of the source text which does not require markup within it.

        """
        anchor = 0
        # The start position of the current substring.
        i = 0
        # The current position in the source text.
        while i <= len(self.source) + 1:
            # current position is a) part of substring
            # b) start of new production
            # c) end of production
            # d) start of document
            if i in self.start_pos or i in self.end_pos or i in self.documents:
                if i in self.documents:
                    if anchor != i:
                        yield ParsedSegment(self.source[anchor:i],
                                            set(self.start_pos[anchor]),
                                            set(self.end_pos[i]),
                                            False)
                        anchor = i
                    else:
                        yield ParsedSegment(self.documents[i],
                                            set(self.start_pos[i]),
                                            set(self.end_pos[i + len(self.documents[i])]),
                                            True)
                        i += len(self.documents[i])
                        anchor = i
                else:
                    if anchor != i:
                        yield ParsedSegment(self.source[anchor:i],
                                            set(self.start_pos[anchor]),
                                            set(self.end_pos[i]),
                                            False)
                        anchor = i
                    i += 1
            else:
                i += 1
        assert anchor >= len(self.source)
        if anchor < len(self.source):
            yield ParsedSegment(self.source[anchor:], set(), set(), False)


# pylint: disable=too-many-instance-attributes
class UTLWithMarkup():
    """A class to represent a piece of UTL code with syntax-directed markup added.

    """

    def __init__(self, source_text: str, markup_start: str='<span class="{}">',
                 markup_end: str='</span><!-- {} -->'):
        self.source = source_text
        self._markup_start = markup_start
        self._markup_end = markup_end
        self.segments = UTLTextParseIterator(self.source)
        self._output = ''  # cached output

    @property
    def text(self) -> str:
        """The `self.source` with inline markup for parts of syntax."""
        if not self._output:
            # cache optimization
            self._output = ''

            for segment in self.segments.parts:
                isinstance(segment, ParsedSegment)
                for start_node in segment.starts:
                    self._output += self.markup_start(start_node.symbol)
                if segment.is_doc:
                    self._output += self.markup_start('document')
                self._output += html.escape(segment.text)
                if segment.is_doc:
                    self._output += self.markup_end('document')
                for end_node in segment.ends:
                    self._output += self.markup_end(end_node.symbol)
            # cache, don't recalc
            self._output = self._output
        return self._output

    def markup_start(self, node: Union[ASTNode, str]) -> str:
        """Returns a string used to start markup for text matched by the production `node`.

        :param ASTNode or str node: A node or string. The first '{}' in `self.markup_start`, or
            any '{0}' string, will be replaced with the value of `node.symbol` if node is an
            ASTNode, or with `node` if it is a string.

        """
        if hasattr(node, "symbol"):
            node = node.symbol
        return self._markup_start.format(node)

    def markup_end(self, node: Union[ASTNode, str]) -> str:
        """Returns a string suitable for ending markup for text matched by the production `node`.

        """
        if hasattr(node, "symbol"):
            node = node.symbol
        # comment after </span> useful for debugging
        return self._markup_end.format(node)
