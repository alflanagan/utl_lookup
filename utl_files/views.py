from django.shortcuts import render
from .models import Package, UTLFile, MacroRef, MacroDefinition


def home(request):
    pkgs = Package.objects.all()
    context = {"packages": pkgs}
    return render(request, 'utl_files/index.html', context)


def search(request, macro_name):
    macros = MacroDefinition.objects.filter(name=macro_name)
    context = {"macros": macros}
    return render(request, 'utl_files/search.html', context)
