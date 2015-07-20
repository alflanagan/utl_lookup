# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def initial_data(apps, schema_editor):
    NewsPaper = apps.get_model("papers", "NewsPaper")
    TNSite = apps.get_model("papers", "TNSite")
    init_news = {'Press of Atlantic City': (),
                 'Atlantic City Weekly': (),
                 'Richmond Times-Dispatch': (('http://richmond.com', 'richmond.com', ), ),
                 'The Mechanicsville Local': (),
                 'Greene County Record': (),
                 'Omaha World-Herald': (),
                 'Winston-Salem Journal': (),
                 'Waco Tribune': (('http://www.wacotrib.com', 'wacotrib.com', ), ),
                 'Charlottesville Daily Progress': (('http://dailyprogress.com', 'dailyprogress.com', ), ),
                 'Greensboro News & Record': (('http://greensboro.com', 'greensboro.com', ), ), }

    news_pk = 0
    site_pk = 0
    for paper in init_news:
        newpaper = NewsPaper(news_pk, paper)
        newpaper.save()
        news_pk += 1
        for site in init_news[paper]:
            newsite = TNSite(site_pk, site[0], site[1], newpaper.id)
            newsite.save()
            site_pk += 1


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_data)
    ]
