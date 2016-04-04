from django.contrib import admin

from .models import TownnewsSite, NewsPaper

class TownnewsSiteAdmin(admin.ModelAdmin):
    list_display = ("URL", "name")

admin.site.register(TownnewsSite, TownnewsSiteAdmin)
admin.site.register(NewsPaper)
