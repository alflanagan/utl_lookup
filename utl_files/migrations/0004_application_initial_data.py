# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-23 20:46
from __future__ import unicode_literals

from django.db import migrations

INITIAL_APPS = ["adowl", "business", "calendar", "classifieds", "editorial", "eedition",
                "electionsstats", "form", "global", "mailinglist", "search", "sportsstats",
                "staticpages", "user", ]


def initial_applications(apps, _):
    Application = apps.get_model("utl_files", "Application")
    # theoretically, at least, this could give applications non-repeatable PKs. But I've never
    # seen it not assign them sequentially.
    for app_name in INITIAL_APPS:
        new_app = Application(name=app_name)
        new_app.full_clean()
        new_app.save()


def unload_applications(apps, _):
    Application = apps.get_model("utl_files", "Application")
    for app_name in INITIAL_APPS:
        the_app = Application.objects.get(name=app_name)
        if the_app:
            the_app.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0003_increase_directory_length'),
    ]

    operations = [
        migrations.RunPython(initial_applications, reverse_code=unload_applications),
    ]
