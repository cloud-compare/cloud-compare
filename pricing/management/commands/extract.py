# Extracts data from master DB to UI helper tables.

# Standard python libraies
import os
import httplib
import zlib
import json
import time
import re

from pprint import pprint

# djnago stuff
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Min

# Our models
from pricing.models import AWS, GCP, UIMain, UIVMSummary

# ##### Utility Functions #####


# Convert a pathname to a flat file name
# eg. /foo/bar.x -> foo.bar.x
def path2name(path):
    npath = path.replace('/', '.')
    if npath[0] == '.':
        npath = npath[1:]
    return npath

# Converts CamelCase to underbars with pre-compiled re's
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def convert_cc(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


class Command(BaseCommand):
    help = 'Extracts data from master tables to UI helper tables'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        # First do the UIMain table

        # Get the stuff we'll need
        aws = AWS.objects.filter(
                                   offer_code='AmazonEC2',
                                   product_family='Compute Instance',
                                   term_type='OnDemand',
                                   tenancy='Shared',
                                   operating_system='Linux', 
                                )

        gcp = GCP.objects.filter(
                                   ptype='COMPUTEENGINE',
                                   psubtype='VMIMAGE',
                                   preemptible=False,
                                )

        # 'small' class is <= 2 GB mem and cpu <= 1


        aws_m = aws.values('instance_type', 'memory', 'vcpu'). \
                    order_by('instance_type').distinct()
        gcp_m = gcp.values('pargs', 'memory', 'cores', 'us').order_by('pargs')
        gcp_m = gcp_m.distinct()

        last_mem = 0.0
        for mem in [2, 4, 8, 16, 32, 64, 128, 256, 512]:

            tclass = '%d-%d' % (last_mem, mem)

            print tclass

            g_band = gcp_m.filter(memory__lte=mem, memory__gt=last_mem)
            for g in g_band:
                gr = UIVMSummary(provider='google',
                                 tclass=tclass,
                                 name=g['pargs'],
                                 memory = g['memory'],
                                 cpu = g['cores'],
                                 price = g['us'],
                                 url='/pricing/gcp/vmimage=%s' % g['pargs']
                                )
                gr.save()

            a_band = aws_m.filter(memory__lte=mem, memory__gt=last_mem)
            for a in a_band:
                ap = aws.filter(instance_type=a['instance_type'],
                                memory__lte=mem, memory__gt=last_mem,
                                price_per_unit__gt=0)

                price=ap.aggregate(Min('price_per_unit'))['price_per_unit__min']

                url='/pricing/aws/offer_code=AmazonEC2/compute_instance=%s' % a['instance_type']
                ar = UIVMSummary(provider='amazon',
                                 tclass=tclass,
                                 name=a['instance_type'],
                                 memory=a['memory'],
                                 cpu=a['vcpu'],
                                 price=price,
                                 url=url,
                                )

                ar.save()


            # Output the main-page record.

            n_gcp = g_band.count()
            n_aws = a_band.count()
            n_azure = 0

            total = n_gcp + n_aws + n_azure

            mr = UIMain(type='VirtMach',
                        tclass=tclass,
                        total=total,
                        gcp=n_gcp,
                        aws=n_aws,
                        azure=n_azure)
            mr.save()

            last_mem = mem

        pass
        # Build AWS look-aside
