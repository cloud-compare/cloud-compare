import os
import httplib
import json
import re

from django.core.management.base import BaseCommand
from django.db.models import Q
from pricing.models import AWS
from pricing.models import GCP

class Command(BaseCommand):

  def add_arguments(self, parser):
    parser.add_argument('command', nargs = 1)


  def handle(self, *args, **options):

    print options['command'][0]

    cmd = options['command'][0]

    if cmd == 'compare':
        # Compare AWS and GCS instances. Try to find matches.

        # apr is AWS queryset
        apr = AWS.objects;
        apr = apr.filter(offer_code = 'AmazonEC2', product_family = 'Compute Instance',
                         term_type = 'OnDemand', tenancy = 'Shared',
                         operating_system = 'Linux')

        gpr = GCP.objects
        gpr = gpr.filter(ptype = 'COMPUTEENGINE', psubtype = 'VMIMAGE', preemptible = False)

        print apr.count(), gpr.count()

        lm = 0.0
        for m in [1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0]:
            print "==== memory <", m
            a_1g = apr.filter(memory__lte = m, memory__gt = lm).order_by('instance_type')
            g_1g = gpr.filter(memory__lte = m, memory__gt = lm)
            print a_1g.count(), g_1g.count()

            for a in a_1g:
                print a.instance_type, a.memory, a.vcpu,  a.price_per_unit, a.location

            for g in g_1g:
                print g.pargs, g.memory, g.cores, g.us, g.asia, g.europe

            lm = m

        return

#    # foreach instance_type
#    #   forech location
#    #    get Windows "Bring your own licence
#    #    get Windows "No License required
#    #    get Wiindows with pre_installed SW required
#    bq = AWS.objects.filter(Q(offer_code = 'AmazonEC2'),
#                            Q(product_family = 'Compute Instance'),
#                            Q(term_type = 'OnDemand'),
#                            Q(tenancy = 'Shared'),
#                            Q(instance_family = 'General purpose'),
#                            Q(current_generation = 'Yes'),
#                            Q(price_per_unit__gt = 0.0))
#    istq = bq.values('instance_type', 'current_generation').order_by('instance_type').distinct()
#    locq = bq.values('location').order_by('location').distinct()
#    
#    for l in locq:
#        for i in istq:
#            base = bq.filter(Q(instance_type = i['instance_type']),
#                             Q(location = l['location']),
#                             Q(license_model = 'Bring your own license'))
#
#            if len(base) == 0:
#                continue
#
#
#            win = bq.filter(Q(instance_type = i['instance_type']),
#                             Q(location = l['location']),
#                             Q(pre_installed_sw = 'NA'),
#                             Q(license_model = 'License Included'))
#            if len(win) == 0:
#                continue
#
#            b = base.first().price_per_unit
#            w = win.first().price_per_unit
#            c = base.first().vcpu
#            m = base.first().memory
#            print '%s,%s,%f,%f,%f,%f,%f' % (l['location'], i['instance_type'], c, m, b, w, (w - b)/b)
