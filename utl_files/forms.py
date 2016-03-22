#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from django import forms
from papers.models import TownnewsSite

# pylint: disable=no-member


class XrefContextForm(forms.Form):
    """A form used to set context (site, global skin, skin) for the UTL cross-reference page."""
    site = forms.ChoiceField(widget=forms.Select(attrs={"class": "form-control"}))
    global_skin = forms.ChoiceField(choices=[])
    app_skin = forms.ChoiceField(choices=[])

    # pylint: disable=too-many-arguments
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, label_suffix=None,
                 empty_permitted=False, field_order=None):
        super().__init__(data, files, auto_id, prefix, initial, label_suffix=label_suffix,
                         empty_permitted=empty_permitted, field_order=field_order)
        # this needs to be init() since it will fail if database tables not created yet
        self.site.choices = [(x.name, x.name) for x in TownnewsSite.objects.all()]
