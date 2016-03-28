#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from django import forms
from crispy_forms.helper import FormHelper, Layout

from .widgets import BSSelect
from papers.models import TownnewsSite

# pylint: disable=no-member


class XrefContextForm(forms.Form):
    """A form used to set context (site, global skin, skin) for the UTL cross-reference page."""
    site = forms.ChoiceField(choices=[], widget=BSSelect())
    global_skin = forms.ChoiceField(choices=[], widget=BSSelect())
    app_skin = forms.ChoiceField(choices=[], widget=BSSelect())

    # pylint: disable=too-many-arguments
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, label_suffix=None,
                 empty_permitted=False, field_order=None):
        super().__init__(data, files, auto_id, prefix, initial, label_suffix=label_suffix,
                         empty_permitted=empty_permitted, field_order=field_order)
        # this needs to be init() since it will fail if database tables not created yet
        self.fields['site'].choices = [(site.URL.replace('http://', ''),
                                        site.URL.replace('http://', ''))
                                       for site in TownnewsSite.objects.all()]
        # # and create our helper instance

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_id = "package-context-form"
        helper.form_method = "get"
        helper.form_action = ""  # do everything with JS
        # # set up bootstrap
        helper.field_template = "utl_files/inline_field.html"
        helper.layout = Layout('site', 'global_skin', 'app_skin')
        # self.helper.help_text_inline = True
        helper.field_class = "col-lg-2"
        helper.form_class = "form-inline"
        return helper
