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
from typing import Union, Sequence, Mapping, Any, Iterable

from utl_lib.ast_node import ASTNode, FrozenASTNode
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_lex_comments import UTLLexerComments


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
        output = ''
        pos = 0
        end = len(self.source)
        com_start_set = set([span[0] for span in self.comments])
        com_end_set = set([span[1] for span in self.comments])

        while pos < end:
            output += self._get_tags(pos)
            if pos in com_end_set:
                output += '</span>'
            if pos in self.docs:
                output += '<span class="document">{}</span>'.format(escape(self.docs[pos]))
                pos += len(self.docs[pos])
                # if last item is document we're at end + 1
                pos = pos if pos <= end else end
                continue
            if pos in com_start_set:
                output += '<span class="comment">'
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
