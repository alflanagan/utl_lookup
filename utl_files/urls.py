# -*- coding:utf-8 -*-

"""utl_lookup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from utl_files import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^macro/(.+)/', views.search, name='search'),
    url(r'api/macro_refs/(.+)/', views.api_macro_refs, name="api_macro_refs"),
    url(r'api/macro_defs/(.+)/', views.api_macro_defs, name="api_macro_defs"),
    url(r'api/applications/', views.api_applications, name="api_applications"),
    url(r'api/packages/', views.api_packages, name="api_pkgs"),
    url(r'api/packages/([^/]+)/', views.api_packages, name="api_pkgs_by_name"),
    url(r'api/packages/([^/]+)/([^/]+)/', views.api_packages, name="api_pkgs_name_version"),
]
