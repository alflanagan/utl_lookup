#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module to provide syntax markup for UTL code.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""

import sys
import re

from html import escape
from warnings import warn
from pathlib import Path
from collections import defaultdict
from typing import Union, Sequence, Mapping, Any, Iterable

from utl_lib.ast_node import ASTNode, FrozenASTNode
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_lex_comments import UTLLexerComments


def merge_mappings_to_lists(dest: Mapping[Any, Sequence],
                            source: Mapping[Any, Iterable]) -> Mapping[Any, Sequence]:
    """Appends items from list in `source[key]` to `dest[key]` if they are not already present,
    for each key in `source`.

    """
    for key in source:
        for item in source[key]:
            if item not in dest[key]:
                dest[key].append(item)
    return dest


class UTLWithMarkup():
    """A class to represent a piece of UTL code with syntax-directed markup added.

    """

    def __init__(self, source_text: str, markup_start: str='<span class="{}">',
                 markup_end: str='</span><!-- {} -->'):
        self.source = source_text
        self.markup_start = markup_start
        self.markup_end = markup_end


    @staticmethod
    def ast_markup_struct(ast_node: ASTNode) -> Sequence[Mapping[int, Sequence[ASTNode]],
                                                         Mapping[int, Sequence[ASTNode]],
                                                         Mapping[int, str]]:
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
                starts, ends, docs = ast_markup_struct(child)
                merge_mappings_to_lists(start_pos, starts)
                merge_mappings_to_lists(end_pos, ends)
                documents.update(docs)
            start_ct = sum([len(start_pos[key]) for key in start_pos])
            end_ct = sum([len(end_pos[key]) for key in end_pos])
            assert start_ct == end_ct
        return (start_pos, end_pos, documents)

    def _markup_start(self, node: Union[ASTNode, str]) -> str:
        """Returns a string used to start markup for text matched by the production `node`.

        :param ASTNode or str node: A node or string. The first '{}' in `self.markup_start`, or
            any '{0}' string, will be replaced with the value of `node.symbol` if node is an
            ASTNode, or with `node` if it is a string.

        """
        if isinstance(node, ASTNode):
            node = node.symbol
        return self.markup_start.format(node)

    def markup_end(node: Union[ASTNode, str]) -> str:
        """Returns a string suitable for ending markup for text matched by the production `node`.

        """
        if isinstance(node, ASTNode):
            node = node.symbol
        # comment after </span> useful for debugging
        return '</span><!-- {} -->'.format(node)



def get_tags(position: int,
             starts: Mapping[int, Sequence[ASTNode]],
             ends: Mapping[int, Sequence[ASTNode]]) -> str:
    """Returns open and/or closing tags for character position `position`.

    :param int position: A character position in the source UTL.

    """
    result = ""
    if position in ends:
        for node in ends[position]:
            result += markup_end(node)
    if position in starts:
        for node in starts[position]:
            result += markup_start(node)
    return result


def build_markup(source_text: str,
                 starts: Mapping[int, Sequence[ASTNode]],
                 ends: Mapping[int, Sequence[ASTNode]],
                 documents: Mapping[int, str],
                 comment_spans: Sequence[Sequence[int]]) -> str:
    """Insert markup into `source_text`, using dictionaries keyed by character position.

    :param source_text: The original text of the parsed program.

    :param starts: character position --> list of AST nodes that begin at that position.

    :param ends: character position --> list of AST nodes that end at that position.

    :param documents: character position --> a segment of text from `source_text`

    :param comment_spans: two-tuples `(start, end)` defining text in `source_text` as comment
        text (note comments have no nodes in AST)

    """
    output = ''
    pos = 0
    end = len(source_text)
    com_start_set = set([span[0] for span in comment_spans])
    com_end_set = set([span[1] for span in comment_spans])

    while pos < end:
        output += get_tags(pos, starts, ends)
        if pos in com_end_set:
            output += '</span>'
        if pos in documents:
            output += '<span class="document">{}</span>'.format(escape(documents[pos]))
            pos += len(documents[pos])
            # if last item is document we're at end + 1
            pos = pos if pos <= end else end
            continue
        if pos in com_start_set:
            output += '<span class="comment">'
        output += source_text[pos]
        pos += 1
    assert pos == end
    if ends:
        max_end = max([key for key in ends])
        # end pos may be after last char
        for i in range(pos, max_end + 1):
            output += get_tags(i, starts, ends)
    return output

def get_comments(some_text: str) -> Sequence[tuple]:
    """Use :py:class:`utl_files.UTLLexerComments` to find comments.

    :param str some_text: UTL source text to pass to lexical analyzer.

    :returns set: Set of tuples of int (start, end) defining characters between start and end as
        part of a comment in `some_text`.

    """
    spans = []
    lexer = UTLLexerComments()
    lexer.input(some_text)
    next_tok = lexer.token()
    while next_tok:
        if next_tok.type == 'COMMENT':
            spans.append((next_tok.lexpos, next_tok.lexpos + len(next_tok.value), ))
        next_tok = lexer.token()
    return tuple(spans)
