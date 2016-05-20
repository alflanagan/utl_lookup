#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


| © 2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
import sys
import re

from warnings import warn
from pathlib import Path

from utl_files.code_markup import UTLWithMarkup

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


def main(filename: str=None) -> None:
    """Parse file in `filename` (or `TEST1` if `filename` is ``None``) and print the contents
    with syntax markup inserted.

    """
    if filename is not None:
        with Path(filename).open('r') as srcin:
            source_text = srcin.read()
    else:
        source_text = TEST1

    marked_up = UTLWithMarkup(source_text)
    the_markup = marked_up.text

    #handlers = [UTLParseHandlerAST()]

    #myparser = UTLParser(handlers)
    #my_ast = FrozenASTNode(myparser.parse(source_text))
    #starts, ends, docs = ast_markup_struct(my_ast)

    #comments = get_comments(source_text)

    check_spans(the_markup)

    with Path('test_data/markup/testmarkup.html').open('r') as template_in:
        template = template_in.read()

    print(template.format(the_markup))


if __name__ == '__main__':
    try:
        main(None if len(sys.argv) < 2 else sys.argv[1])
    except Exception:
        if len(sys.argv) > 1:
            sys.stderr.write("Error processing file {}.".format(sys.argv[1]))
        raise
