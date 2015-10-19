from django.shortcuts import render
from .models import Package, UTLFile, MacroRef, MacroDefinition

# Create your views here.
def home(request):
    pkgs = Package.objects.all();
    context = {"packages": pkgs}
    return render(request, 'utl_files/index.html', context)
