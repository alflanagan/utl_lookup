from django.contrib import admin

# Register your models here.
from .models import Application, TNSite, Package, UTLFile

admin.site.register(Application)
admin.site.register(TNSite)
admin.site.register(Package)
admin.site.register(UTLFile)
