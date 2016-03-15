#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from django import forms
from papers.models import TNSite


class XrefContextForm(forms.Form):
    """A form used to set context (site, global skin, skin) for the UTL cross-reference page."""
    site = forms.ChoiceField(widget=forms.Select(attrs={"class": "form-control"}),
                             choices=[(x.name, x.name) for x in TNSite.objects.all()])
    global_skin = forms.ChoiceField(choices=[])
    app_skin = forms.ChoiceField(choices=[])
