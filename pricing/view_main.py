from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.db.models import Count

from django.db import connection

def main(request):
    items = []
 
    args = {'body_title': 'Main', 'items': items}
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

