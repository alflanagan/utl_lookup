#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URLs for application :py:mod:`papers`.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from django.conf.urls import url

from . import views

urlpatterns = [url(r'^$', views.index, name='index'), ]
