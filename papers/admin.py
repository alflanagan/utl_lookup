#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin site registrations for :py:mod:`papers`.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from django.contrib import admin

from .models import TownnewsSite, NewsPaper


class TownnewsSiteAdmin(admin.ModelAdmin):
    """Customize display for admin of :py:class:`papers.TownnewsSite` objects."""
    list_display = ("URL", "name")


admin.site.register(TownnewsSite, TownnewsSiteAdmin)
admin.site.register(NewsPaper)
