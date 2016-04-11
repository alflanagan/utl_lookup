#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
View functions for :py:mod:`papers`.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
# pylint: disable=no-member

from django.shortcuts import render, get_object_or_404

from jsonview.decorators import json_view

from .models import NewsPaper, TownnewsSite


def index(request):
    """Main page for the site, quick access to search functionality."""
    context = {"papers": NewsPaper.objects.all().order_by('name')}  # pylint: disable=E1101
    return render(request, 'papers/index.html', context=context)


@json_view
def api_sites(_, paper=None):
    """List Townnews Sites in system."""
    result = []
    if paper is None:
        query = TownnewsSite.objects.all()
    else:
        paper = get_object_or_404(NewsPaper, name=paper)
        query = TownnewsSite.objects.filter(paper=paper)

    for site in query:
        result.append({"URL": site.URL, "name": site.name, "paper": site.paper.name, })
    return result
