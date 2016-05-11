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


def markup(cssclass, some_string):
    """Return ``some_string`` wrapped in a <span> element with CSS class == ``cssclass``."""
    return '<span class="{}">{}</span>'.format(cssclass, some_string)


def interleave(parent_node, subst_kids, source_text):
    """Returns the result of taking the source_text matching `parent_node` and substituting the
    text in the array `subst_kids` for the text matching each child of `parent_node`.

    TODO: add long example here
    """
    assert isinstance(parent_node, ASTNode)
    kids = [node for node in parent_node.children
            if not (node.attributes["start"] == 0 and node.attributes["end"] == 0)]
    assert len(kids) == len(subst_kids)
    first_part = source_text[parent_node.attributes["start"]:
                             kids[0].attributes["start"]]
    last_part = source_text[kids[-1].attributes["end"]:
                            parent_node.attributes["end"]]
    # marked up text == part before first child + ...
    results = [first_part]
    for index in range(len(kids) - 1):
        # add marked-up text
        results.append(subst_kids[index])
        # fill back in any missed chars
        results.append(source_text[kids[index].attributes["end"]:
                                   kids[index + 1].attributes["start"]])
    # don't leave out last marked up item
    results.append(subst_kids[-1])
    # and any text after last child
    results.append(last_part)
    return "".join(results)


def ast_markup(ast_node: ASTNode, source_text: str):  # pylint: disable=R0912
    """Return the part of `source_text` matching `ast_node` with syntax markup added."""
    kids = [ast_markup(kid, source_text) for kid in ast_node.children
            if not (kid.attributes["start"] == 0 and kid.attributes["end"] == 0)]
    result = ""

    if ast_node.symbol == 'utl_doc':
        result = markup("utl-doc", interleave(ast_node, kids, source_text))
    elif ast_node.symbol == "macro_defn":
        result = markup("macro-defn", interleave(ast_node, kids, source_text))
    elif ast_node.symbol == 'document':
        assert len(kids) == 0
        result = markup('html_doc', escape(ast_node.attributes["text"]))
    elif ast_node.symbol == 'id':
        parts = [ast_node.attributes["symbol"]]
        # if there are children, kids has marked-up items, but we only want markup
        # around entire ID. so abandon those markups, create new one
        parts.extend([node.attributes["symbol"] for node in ast_node.children])
        result = markup('identifier', ".".join(parts))
    elif ast_node.symbol == "macro_decl":
        mname = ast_node.attributes["name"]
        mtext = source_text[ast_node.attributes["start"]:ast_node.attributes["end"]]
        other_parts = mtext.split(mname)
        result = markup("macro-decl", other_parts[0] + markup("macro_name", mname) + other_parts[1])
    elif ast_node.symbol == "statement_list":
        result = "".join([kid for kid in kids if kid is not None])
    elif ast_node.symbol == "else":
        if not kids:
            result = ""
        else:
            result = markup("else", interleave(ast_node, kids, source_text))
    elif ast_node.symbol == "elseif_stmts":
        if not kids:
            result = ""
        else:
            result = markup("elseif", interleave(ast_node, kids, source_text))
    elif ast_node.symbol == "if":
        result = markup("if_stmt", interleave(ast_node, kids, source_text))
    else:
        warn("AST symbol not recognized: " + ast_node.symbol)
        result = ""
    return result


def merge_mappings_to_lists(dest, source):
    """If `dest` and `source` are mappings from a key to a list, adds each item in each list in
    `source` to the list indexed by the same key in `dest`.

    """
    for key in source:
        for item in source[key]:
            if item not in dest[key]:
                dest[key].append(item)
    return dest


def ast_markup_struct(ast_node):
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
        if not ast_node.attributes["start"] == ast_node.attributes["end"] == 0:
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


def get_tags(position, starts, ends):
    """Returns open and/or closing tags for character position `position`.

    :param int position: A character position in the source UTL.

    """
    result = ""
    if position in ends:
        for node in ends[position]:
            result += '</span><!-- {} -->'.format(node.symbol)
    if position in starts:
        for node in starts[position]:
            result += '<span class="{}">'.format(node.symbol)
    return result


def build_markup(source_text, starts, ends, documents, comment_spans):
    """Insert markup into `source_text`, using dictionaries keyed by character position.

    :param str source_text: The original text of the parsed program.

    :param dict starts: A mapping from character position to a list of AST nodes that begin at
        that position.

    :param dict ends: A mapping from character position to a list of AST nodes that end at that
        position.

    :param dict documents: A mapping from character position to a segment of text.

    :param iterable comment_spans: A sequence of two-tuples `(start, end)` defining text in
        source_text as comment text (must be separate as they don't get AST nodes).

    """
    output = ''
    pos = 0
    end = len(source_text) - 1
    com_start_set = set([span[0] for span in comment_spans])
    com_end_set = set([span[1] for span in comment_spans])

    while pos < end:
        output += get_tags(pos, starts, ends)
        if pos in com_end_set:
            output += '</span>'
        if pos in documents:
            output += '<span class="document">{}</span>'.format(escape(documents[pos]))
            pos += len(documents[pos])
            continue
        if pos in com_start_set:
            output += '<span class="comment">'
        output += source_text[pos]
        pos += 1
    assert pos == end
    max_end = max([key for key in ends])
    for i in range(pos, max_end+1):
        for end in ends[i]:
            output += '</span><!-- {} -->'.format(end.symbol)
    # ends can be after last character in source
    # output += '</span>' * len(ends[len(source_text) + 1])
    return output


def check_spans(some_text):
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


def get_comments(some_text):
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


def main(filename=None):
    """Parse file in `filename` (or `TEST1` if `filename` is ``None``) and print the contents
    with syntax markup inserted.

    """
    if filename is not None:
        with Path(filename).open('r') as srcin:
            source_text = srcin.read()
    else:
        source_text = TEST1

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
    with Path('test_data/markup/testmarkup.html').open('r') as template_in:
        template = template_in.read()
#
    print(template.format(the_markup))


if __name__ == '__main__':
    main(None if len(sys.argv) < 2 else sys.argv[1])
