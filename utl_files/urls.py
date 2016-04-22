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
from django.conf.urls import url
from utl_files import views

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^demo/$', views.demo, name='demo'),

    # search(request, macro_name)
    url(r'^macro/(.+)/', views.search, name='search'),

    # api_macro_refs(_, macro_name)
    url(r'api/macro_refs/(.+)/', views.api_macro_refs, name="api_macro_refs"),

    # api_macro_defs(_, macro_name, pkg_name=None, pkg_version=None, file_path=None)
    url(r'api/macro_defs/([^/]+)/([^/]+)/([^/]+)/(.+)/', views.api_macro_defs,
        name="api_macro_defs_file"),
    url(r'api/macro_defs/([^/]+)/([^/]+)/([^/]+)/', views.api_macro_defs,
        name="api_macro_defs_ver"),
    url(r'api/macro_defs/([^/]+)/([^/]+)/', views.api_macro_defs, name="api_macro_defs_pkg"),
    url(r'api/macro_defs/([^/]+)/', views.api_macro_defs, name="api_macro_defs"),

    # api_macro_text(_, macro_id)
    url(r'api/macro_def_text/(\d+)/', views.api_macro_text, name="api_macro_text"),

    # api_applications(_)
    url(r'api/applications/', views.api_applications, name="api_applications"),

    # api_packages(_, name=None, version=None)
    url(r'api/packages/([^/]+)/([^/]+)/', views.api_packages, name="api_pkgs_name_version"),
    url(r'api/packages/([^/]+)/', views.api_packages, name="api_pkgs_by_name"),
    url(r'api/packages/', views.api_packages, name="api_pkgs"),

    # api_global_skins_for_site(_, site_url)
    url(r'api/global_skins_for_site/([^/]+)/', views.api_global_skins_for_site,
        name="api_global_skins_for_site"),

    # api_app_skins_for_site(_, site_url)
    url(r'api/app_skins_for_site/([^/]+)/', views.api_app_skins_for_site,
        name="api_app_skins_for_site"),

    # api_packages_for_site_with_skins(_, site_domain, global_pkg_name, skin_app, skin_name):
    url(r'api/packages_for_site_with_skins/([^/]+)/([^/]+)/([^/]+)/([^/]+)',
        views.api_packages_for_site_with_skins,
        name="api_packages_for_site_with_skins"),

    # api_package_files_certified(_, pkg_name, pkg_version=None):
    url(r'api/package_files/certified/([^/]+)/([^/]+)/',
        views.api_package_files_certified,
        name="api_package_files_certified"),
    url(r'api/package_files/certified/([^/]+)/',
        views.api_package_files_certified,
        name="api_package_files_certified_fromname"),

    # api_package_files_custom(_, site_url, pkg_name=None)
    url(r'api/package_files/([^/]+)/([^/]+)',
        views.api_package_files_custom,
        name="api_package_files_custom"),

]  # yapf: disable
