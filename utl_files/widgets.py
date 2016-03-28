#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom widgets to work with bootstrap3 (if no suitable widget in django-crispy-forms.bootstrap)

| © 2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
import copy

from django.forms.widgets import Widget, flatatt, format_html, force_text, mark_safe, chain


class BSSelect(Widget):
    """A custom widget to render a selection as bootstrap button dropdown
    (http://getbootstrap.com/components/#btn-dropdowns). Curiously :py:mod:`crispy_forms` seems
    not to cover this case.

    """
    allow_multiple_selected = False

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs)
        # choices can be any iterable, but we may need to render this widget
        # multiple times. Thus, collapse it into a list so it can be consumed
        # more than once.
        self.choices = list(choices)

    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.attrs = self.attrs.copy()
        obj.choices = copy.copy(self.choices)
        memo[id(self)] = obj
        return obj

    def render(self, name, value, attrs=None, choices=()):  # pylint: disable=W0221
        """Render the widget as a list ``<ul>`` with attributes ``attr``, list items from
        ``choices``, and the choice equal to ``value`` selected.

        """
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        try:
            final_attrs["class"] += " dropdown-menu"
            # unpleasant hack to remove class forced by crispy field tag
            # the fix in CSS is ... messy. new tag??
            final_attrs["class"] = final_attrs["class"].replace("form-control", "")
        except KeyError:
            final_attrs["class"] = "dropdown-menu"
        output = [format_html('<ul{}>', flatatt(final_attrs))]
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append('</ul>')
        return mark_safe('\n'.join(output))

    def render_option(self, selected_choices, option_value, option_label):
        """Render a single option as a list item <li>."""
        if option_value is None:
            option_value = ''
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' class="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html('<li{}>{}</li>',
                           selected_html,
                           force_text(option_label))

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                # output.append(format_html('<optgroup label="{}">', force_text(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                # output.append('</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)
