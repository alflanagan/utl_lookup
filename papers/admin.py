from django.contrib import admin

from .models import TNSite, NewsPaper


# Register your models here.
admin.site.register(TNSite)
admin.site.register(NewsPaper)
