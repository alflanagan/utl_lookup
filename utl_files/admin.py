#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module to register classes from :py:mod:`utl_files` for the admin application.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
from django.contrib import admin

# Register your models here.
from .models import (Application, CertifiedUsedBy, Package, UTLFile, PackageDep, PackageProp,
                     MacroRef, MacroDefinition)

@admin.register(Package)
class PkgManager(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'pkg_type', 'app', 'last_download', 'disk_directory',
                           'is_certified', ),}),
        ('If Certified', {'fields': ('version', ),}),
        ('If Custom', {'fields': ('site', ),})
    )

admin.site.register(Application)
admin.site.register(CertifiedUsedBy)
admin.site.register(UTLFile)
admin.site.register(PackageDep)
admin.site.register(PackageProp)
admin.site.register(MacroRef)
admin.site.register(MacroDefinition)
