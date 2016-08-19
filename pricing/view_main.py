from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.db.models import Q
from django.db.models import Count

from django.db import connection

from pprint import pprint

from models import UIMain, UIVMSummary

from view_gcp import get_gcp_vmimage
from view_aws import get_aws_compute_instance

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

    # Get the Virtual Machines.
    uim = UIMain.objects.filter(type='VirtMach')
    uim = uim.values('tclass', 'total')
    print uim

    items = {}
    for u in uim:
        tclass = u['tclass']
        print tclass
        uis = UIVMSummary.objects.filter(tclass=tclass)
        uis = uis.order_by('memory', 'cpu')
        uis = uis.values('provider', 'tclass', 'name', 'memory', 'cpu', 'price')

        #todo #### Setup next level struct for the modal
        
        item = {'summary': uis}
        for ui in uis:
          print ui['provider']
          if ui['provider'] == 'google':
              ui['details'] = get_gcp_vmimage(ui['name'])
          elif ui['provider'] == 'amazon':
              ui['details'] = get_aws_compute_instance(ui['name'])
          else:
              ui['details'] = None

        u['items'] = uis

    args = {'body_title': 'Main', 'items': uim}
    return render(request, 'bootstrap_main.html', args)


def class_list(request, type, provider, tclass):
    print type, provider, tclass

    if type != 'VirtMach':
        raise Http404('type is not "VirtMach"')

    uis = UIVMSummary.objects.filter(tclass=tclass)

    if provider != 'all':
        uis = uis.filter(provider=provider)

    uis = uis.order_by('memory', 'cpu')

    args = {'tclass': tclass, 'provider': provider, 'items': uis}
    return render(request, 'bootstrap_vmlist.html', args)
     

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

