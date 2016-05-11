#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


| © 2016 BH Media Group, Inc.
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

TEST1 = """[%
macro custom_uiTabControl();
/* UI tab control */%]
<script>
       // control tabs
        $("#homes-tabs").tabs().show();
        $(".block.real-estate-search").removeClass("blox-loading");
        $("#homes-tabs-2, #homes-tabs-3").hide();

        // jQuery tabs fails to function so we make our own
        $("#homes-tabs .ui-tabs-panel").css({'padding' : '0px'});

        $("#ui-id-2").click(function() {
                $("#homes-tabs-1").show();
                $("#homes-tabs-2, #homes-tabs-3").hide();
        });
        $("#ui-id-3").click(function() {
                $("#homes-tabs-2").show();
\t\t$("#homes-tabs-1, #homes-tabs-3").hide();
        });
        $("#ui-id-4").click(function() {
                $("#homes-tabs-3").show();
                $("#homes-tabs-1, #homes-tabs-2").hide();
        });

        $("#extra-features-toggle").click(function() {
          $(".extra-features").toggle();
        });[% if stab %]
        $("#ui-id-[% stab %]").click();
        [% end %]
    </script>
[%-
end %]
"""

TEST2 = """<div id="blox-right-col" class="grid_2 omega">
        <img src="global/resources/images/_site/powerup.jpg">
</div>
"""

TEST3 = ("[%- /* to use the default member-benefits text, "
         "change the name of this file, or remove it. */ -%]")


class UTLSourceCode():
    """Represents a piece of UTL source code, providing lexing, parsing, markup, etc.

    :param str source: One or mile lines of UTL source code.

    """

    def __init__(self, source: str) -> None:
        self.source = source
        self.ast = None


def merge_mappings_to_lists(dest: Mapping[Any, Sequence],
                            source: Mapping[Any, Iterable]) -> Mapping[Any, Sequence]:
    """If `dest` and `source` are mappings from a key to a list, adds each item in each list in
    `source` to the list indexed by the same key in `dest`.

    """
    for key in source:
        for item in source[key]:
            if item not in dest[key]:
                dest[key].append(item)
    return dest


def ast_markup_struct(ast_node: ASTNode) -> Sequence[Mapping[int, Sequence[ASTNode]],
                                                     Mapping[int, Sequence[ASTNode]],
                                                     Mapping[int, str]]:
    """Walks tree rooted on `ast_node`. Returns a tuple containing:
    1. a dictionary mapping starting character offsets to AST nodes, and
    2. a ditionary mapping ending character offsets to AST nodes.

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


# The actual text used for markup is localized to these two procedures, so we can easily change
# to another method
def markup_start(node: Union[ASTNode, str]) -> str:
    """Returns a string used to start markup for text matched by the production `node`.

    :param ASTNode or str node: A node in an AST tree produced from UTL parse

    """
    if isinstance(node, ASTNode):
        node = node.symbol
    return '<span class="{}">'.format(node)


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


def check_spans(some_text: str) -> None:
    """Performs validation on '&lt;span&gt;' tags in `some_text`. Reports open tags with no
    closing tag, or closing tags with no open.

    """
    span_re = re.compile(r'<span ')
    span_end_re = re.compile(r'</span')
    span_count = len(span_re.findall(some_text))
    end_count = len(span_end_re.findall(some_text))
    if span_count > end_count:
        warn("missing {} end tags".format(span_count - end_count))
    elif span_count < end_count:
        warn("extra {} end tags!".format(end_count - span_count))


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


def main(filename: str=None) -> None:
    """Parse file in `filename` (or `TEST1` if `filename` is ``None``) and print the contents
    with syntax markup inserted.

    """
    if filename is not None:
        with Path(filename).open('r') as srcin:
            source_text = srcin.read()
    else:
        source_text = TEST2

    handlers = [UTLParseHandlerAST()]

    myparser = UTLParser(handlers)
    my_ast = FrozenASTNode(myparser.parse(source_text))
    starts, ends, docs = ast_markup_struct(my_ast)

    comments = get_comments(source_text)


#     def print_struct(map_int_to_list):
#         print('-'*40)
#         sort_keys = list(map_int_to_list.keys())
#         sort_keys.sort()
#         for key in sort_keys:
#             print(key)
#             for node in map_int_to_list[key]:
#                 print("\t{}".format(node))
#
#     print_struct(starts)
#     print_struct(ends)
#     print('-'*40)
#     for key in docs:
#         print(key, key + len(docs[key]))

    the_markup = build_markup(source_text, starts, ends, docs, comments)
#
    check_spans(the_markup)
#
#     with Path('test_data/markup/testmarkup.html').open('r') as template_in:
#         template = template_in.read()

#     print(template.format(the_markup))


if __name__ == '__main__':
    try:
        main(None if len(sys.argv) < 2 else sys.argv[1])
    except Exception:
        if len(sys.argv) > 1:
            sys.stderr.write("Error processing file {}.".format(sys.argv[1]))
        raise
