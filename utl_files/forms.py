#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from django import forms
from django.forms.utils import ErrorList

from papers.models import TNSite


class XrefContextForm(forms.Form):
    """A form used to set context (site, global skin, skin) for the UTL cross-reference page."""
    site = forms.ChoiceField(widget=forms.Select(attrs={"class": "form-control"})
                             # using query to initialize class variable breaks "manage.py migrate"
                             # if tables not created yet.
                             # ,choices=[(x.name, x.name) for x in TNSite.objects.all()])
                            )
    global_skin = forms.ChoiceField(choices=[])
    app_skin = forms.ChoiceField(choices=[])

    # pylint: disable=too-many-arguments
    def __init__(self, data=None, files=None, auto_id=None, prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, field_order=None):
        """Customized to set up choices for fields after class creation time."""
        super().__init__(data=data, files=files, auto_id=auto_id, prefix=prefix,
                         initial=initial, error_class=error_class, label_suffix=label_suffix,
                         empty_permitted=empty_permitted, field_order=field_order)
        self.fields["site"].choices = [(x.name, x.name) for x in TNSite.objects.all()] # pylint: disable=no-member
