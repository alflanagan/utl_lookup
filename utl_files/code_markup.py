#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module to provide syntax markup for UTL code.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""


from html import escape
from collections import defaultdict
from typing import Union, Sequence, Mapping, Any, Iterable, Iterator, Tuple

from utl_lib.ast_node import ASTNode, FrozenASTNode
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_lex_comments import UTLLexerComments


class UTLTextParseIterator():  # pylint: disable=R0903
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
        self.parser = UTLParser([UTLParseHandlerAST()])
        self.source = source_text
        self.parse_tree = FrozenASTNode(self.parser.parse(self.source))
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
        isinstance(self.parse_tree, ASTNode)
        for ast_node in self.parse_tree.walk():
            isinstance(ast_node, ASTNode)
            if ast_node.symbol == 'document':
                assert not ast_node.children
                self.documents[ast_node.attributes["start"]] = ast_node.attributes["text"]
            else:
                # omit productions that didn't match any text
                if not ast_node.attributes["start"] == ast_node.attributes["end"]:
                    self.start_pos[ast_node.attributes["start"]].append(ast_node)
                    self.end_pos[ast_node.attributes["end"]].append(ast_node)

        # basic sanity check: # starts == # ends
        start_ct = sum([len(self.start_pos[key]) for key in self.start_pos])
        end_ct = sum([len(self.end_pos[key]) for key in self.end_pos])
        assert start_ct == end_ct

    @property
    def parts(self) -> Iterator[Tuple[str, Sequence[ASTNode], Sequence[ASTNode], bool]]:
        """Returns an iterator which returns a tuple for each substring of
        the source text which does not require markup within it.

        """
        anchor = 0
        # The start position of the current substring.
        i = 0
        # The current position in the source text.
        while i <= len(self.source):
            # current position is a) part of substring
            # b) start of new production
            # c) end of production
            # d) start of document
            if i in self.start_pos or i in self.end_pos or i in self.documents:
                if i in self.documents:
                    if anchor != i:
                        yield (self.source[anchor:i],
                               set(self.start_pos[anchor]),
                               set(self.end_pos[i]),
                               False, )
                        anchor = i
                    else:
                        yield (self.documents[i],
                               set(self.start_pos[i]),
                               set(self.end_pos[i + len(self.documents[i])]),
                               True, )
                        i += len(self.documents[i])
                        anchor = i
                else:
                    if anchor != i:
                        yield (self.source[anchor:i],
                               set(self.start_pos[anchor]),
                               set(self.end_pos[i]),
                               False, )
                        anchor = i
                    i += 1
            else:
                i += 1
        if anchor < len(self.source):
            yield(self.source[anchor:], set(), set(), False)


# pylint: disable=too-many-instance-attributes
class UTLWithMarkup():
    """A class to represent a piece of UTL code with syntax-directed markup added.

    """

    # class-level objects that only need to be created once
    HANDLERS = [UTLParseHandlerAST()]

    PARSER = UTLParser(HANDLERS)

    def __init__(self, source_text: str, markup_start: str='<span class="{}">',
                 markup_end: str='</span><!-- {} -->'):
        self.source = source_text
        # PROBLEM: source_text may have embedded HTML, which must be escaped
        # after the markup, while the markup itself is not escaped:
        # source_text = '<p>this is a UTL document</p>'
        # UTLWithMarkup(source_text).text ==
        # '<span class="document">&lt;p&gt;this is a UTL document&lt;/p&gt;'
        # '</span><!-- document -->'

        # self.source = html.escape(self.source, quote=False)
        # can't do that because
        # [% if a > b; %] !=> [% if a &gt; b; %]

        # so we call escape() only for "documents". Why is that not working...
        # must do it for literal strings to... Damn
        # [% echo "<span>"; %] ==> [% echo "&lt;span&gt;"; %]
        # to display correctly in browser
        self._markup_start = markup_start
        self._markup_end = markup_end
        self.top_node = FrozenASTNode(self.PARSER.parse(self.source))
        self.starts, self.ends, self.docs = self._ast_markup_struct(self.top_node)
        self.comments = self._get_comments()

    @staticmethod
    def _merge_mappings_to_lists(dest: Mapping[Any, Sequence],
                                 source: Mapping[Any, Iterable]) -> Mapping[Any, Sequence]:
        """Appends items from list in `source[key]` to `dest[key]` if they are not already present,
        for each key in `source`.

        """
        for key in source:
            for item in source[key]:
                if item not in dest[key]:
                    dest[key].append(item)
        return dest

    @classmethod
    def _ast_markup_struct(cls, ast_node: ASTNode) -> Sequence[Mapping]:
        """For the tree rooted at `ast_node`, build dictionaries for start positions, end positions,
        and documents.

        :param ast_node: An :py:class:`~utl_lib.ast_node.ASTNode` rooting a tree of sytnax
            productions.

        :returns tuple: A tuple containing the following:

            1. A dictionary from starting character positions to a sequence of all nodes that start
               at that positon,

            2. A dictionary from starting character positions to a sequence of all nodes that end at
               that position,

            3. A dictionary from a document starting character position to the text of the document.

        """
        isinstance(ast_node, ASTNode)
        start_pos = defaultdict(list)
        end_pos = defaultdict(list)
        documents = {}
        if ast_node.symbol == 'document':
            assert not ast_node.children
            documents[ast_node.attributes["start"]] = ast_node.attributes["text"]
        else:
            # omit productions that didn't match any text
            if not ast_node.attributes["start"] == ast_node.attributes["end"]:
                start_pos[ast_node.attributes["start"]].append(ast_node)
                end_pos[ast_node.attributes["end"]].append(ast_node)
            for child in ast_node.children:
                starts, ends, docs = cls._ast_markup_struct(child)
                cls._merge_mappings_to_lists(start_pos, starts)
                cls._merge_mappings_to_lists(end_pos, ends)
                documents.update(docs)
            start_ct = sum([len(start_pos[key]) for key in start_pos])
            end_ct = sum([len(end_pos[key]) for key in end_pos])
            assert start_ct == end_ct
        return (start_pos, end_pos, documents)

    def _build_markup(self) -> str:
        """Returns the contents of `self.source`, with additional tags
        for semantic markup.
        """
        # TODO: Must redo this. we need to build list of parts between added
        # tags so that those parts can be html-escaped
        output = ''
        pos = 0
        end = len(self.source)
        com_start_set = set([span[0] for span in self.comments])
        com_end_set = set([span[1] for span in self.comments])

        while pos < end:
            output += self._get_tags(pos)
            if pos in com_end_set:
                output += self.markup_end("comment")
            if pos in self.docs:
                output += '{}{}{}'.format(self.markup_start("document"),
                                          escape(self.docs[pos]),
                                          self.markup_end("document"))
                pos += len(self.docs[pos])
                # if last item is document we're at end + 1
                pos = pos if pos <= end else end
                continue
            if pos in com_start_set:
                output += self.markup_start("comment")
            output += self.source[pos]
            pos += 1
        assert pos == end
        if self.ends:
            max_end = max([key for key in self.ends])
            # end pos may be after last char
            for i in range(pos, max_end + 1):
                output += self._get_tags(i)
        return output

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

    def _get_tags(self, position: int) -> str:
        """Returns open and/or closing tags for character position `position`.

        :param int position: A character position in the source UTL.

        """
        result = ""
        if position in self.ends:
            for node in self.ends[position]:
                result += self.markup_end(node)
        if position in self.starts:
            for node in self.starts[position]:
                result += self.markup_start(node)
        return result

    @property
    def text(self) -> str:
        """The `self.source` with inline markup for parts of syntax."""
        return self._build_markup()
