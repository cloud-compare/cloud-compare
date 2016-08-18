from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.db.models import Count

from django.db import connection

from pprint import pprint

class VMType():
    def __init__(self, name, gcp, aws, azure):
        self.name = name
        self.aws = aws
        self.gcp = gcp
        self.azure = azure

    def __repr__(self):
        return self.name + " " + str(self.aws) + " " +  str(self.gcp) + " " +  str(self.azure)

    def name(self):
        return self.name

    def gcp(self):
        return self.gcp

    def aws(self):
        return self.aws

    def azure(self):
        return self.azure
    

def main(request):
    vmtypes = []
    vmtypes.append(VMType('small', True, True, True))
    vmtypes.append(VMType('standard', True, True, True))
    vmtypes.append(VMType('high cpu', True, True, True))
    vmtypes.append(VMType('storage', False, True, False))
    vmtypes.append(VMType('gpu', False, True, False))
    pprint(vmtypes)
 
    items = {'vmtypes' : vmtypes}
    args = {'body_title': 'Main', 'vmtypes': vmtypes, 'items': items}
    return render(request, 'bootstrap_main.html', args)

def about(request):
    args = {}
    return render(request, "bootstrap_about.html", args)


def error400(request):
    args = {}
    return render(request, "bootstrap_error.html", args)


def error403(request):
    args = {}
    return render(request, "bootstrap_error.html", args)


def error404(request):
    args = {}
    return render(request, "bootstrap_error.html", args)


def error500(request):
    args = {}
    return render(request, "bootstrap_error.html", args)

