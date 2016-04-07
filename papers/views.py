#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
View functions for :py:mod:`papers`.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from django.shortcuts import render

from .models import NewsPaper


def index(request):
    """Main page for the site, quick access to search functionality."""
    context = {"papers": NewsPaper.objects.all().order_by('name')}  # pylint: disable=E1101
    return render(request, 'papers/index.html', context=context)
