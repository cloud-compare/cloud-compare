from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.db.models import Q
from django.db.models import Count

from django.db import connection

from pprint import pprint

from models import UIMain, UIVMSummary

from view_gcp import get_gcp_vmimage
from view_aws import get_aws_compute_instance
    

# Handles main
def main(request):
    """Build main page."""

    # Get the Virtual Machines.
    uim = UIMain.objects.filter(type='VirtMach')
    uim = uim.values('tclass', 'total')

    # Get the catagory bands
    items = {}
    for u in uim:
        tclass = u['tclass']
        uis = UIVMSummary.objects.filter(tclass=tclass)
        uis = uis.order_by('cpu', 'price', 'memory')
        uis = uis.values()

        item = {'summary': uis}
        for ui in uis:
          if ui['provider'] == 'google':
              ui['details'] = get_gcp_vmimage(ui['name'])
          elif ui['provider'] == 'amazon':
              ui['details'] = get_aws_compute_instance(ui['name'])
          else:
              ui['details'] = None

        u['items'] = uis

    args = {'body_title': 'Main', 'items': uim}
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

