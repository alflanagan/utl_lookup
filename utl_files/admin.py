from django.contrib import admin

# Register your models here.
from .models import Application, Package, UTLFile, PackageDep, PackageProp

admin.site.register(Application)
admin.site.register(Package)
admin.site.register(UTLFile)
admin.site.register(PackageDep)
admin.site.register(PackageProp)
