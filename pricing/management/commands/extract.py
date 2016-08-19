# Extracts data from master DB to UI helper tables.

# Standard python libraies
import os
import httplib
import zlib
import json
import time
import re

# djnago stuff
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Min, Max

# Our models
from pricing.models import AWS, GCP, UIMain, UIVMSummary, UIAWSSummary

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

# Gets the Min/Max price for a particular
# Reserved term combination
def get_aws_rsv_prices(query, obj, poption, unit, minname, maxname):
    # partial upfront
    min_price = query.filter(purchase_option=poption, unit=unit). \
                    aggregate(Min('price_per_unit'))['price_per_unit__min']
    max_price = query.filter(purchase_option='All Upfront'). \
                  aggregate(Max('price_per_unit'))['price_per_unit__max']
    setattr(obj, minname, min_price)
    setattr(obj, maxname, max_price)
    pass


class Command(BaseCommand):
    help = 'Extracts data from master tables to UI helper tables'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        # First do the UIMain table

        print 'Build Main Lookaside'
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


        aws_m = aws.values('instance_type', 'memory', 'vcpu'). \
                    order_by('instance_type').distinct()
        gcp_m = gcp.values('pargs', 'memory', 'cores', 'us').order_by('pargs')
        gcp_m = gcp_m.distinct()

        last_mem = 0.0
        for mem in [2, 4, 8, 16, 32, 64, 128, 256, 512]:

            tclass = '%d-%d' % (last_mem, mem)

            print '  class:', tclass

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

        # Build AWS look-aside
        # Start again with aws query
        print 'Build AWS Lookaside'
        aws = AWS.objects.filter(
                                   offer_code='AmazonEC2',
                                   product_family='Compute Instance',
                                   operating_system='Linux', 
                                )
        anames = aws.values('instance_type'). \
                     order_by('instance_type').distinct()

        # Do queries for each name to extract entry
        for an in anames:
            # query for this instance
            name = an['instance_type']
            print '  ', name

            name_q = aws.filter(
                          instance_type=name,
                          operating_system='Linux',
                          price_per_unit__gt=0)

            # Get common stuff
            nc = name_q[0]
            uar = UIAWSSummary(
                       name=name, memory=nc.memory, vcpu=nc.vcpu,
                       physical_processor=nc.physical_processor,
                       clock_speed=nc.clock_speed,
                       current_generation=nc.current_generation,
                       network_performance=nc.network_performance,
                       storage=nc.storage,
                       dedicated_ebs_throughput=nc.dedicated_ebs_throughput,
                    )

            # Get OnDemand, Shared Pricing for this instance type
            od = name_q.filter(term_type='OnDemand', tenancy='Shared')
            min_price = od.aggregate(Min('price_per_unit'))['price_per_unit__min']
            max_price = od.aggregate(Max('price_per_unit'))['price_per_unit__max']
            setattr(uar, 'on_demand_shared_low', min_price)
            setattr(uar, 'on_demand_shared_high', max_price)

            # Get OnDemand, Dedicated Pricing for this instance type
            od = name_q.filter(term_type='OnDemand', tenancy='Dedicated')
            min_price = od.aggregate(Min('price_per_unit'))['price_per_unit__min']
            max_price = od.aggregate(Max('price_per_unit'))['price_per_unit__max']
            setattr(uar, 'on_demand_dedicated_low', min_price)
            setattr(uar, 'on_demand_dedicated_high', max_price)

            # Reserved 1yr, Shared
            od = name_q.filter(term_type='Reserved',
                               tenancy='Shared',
                               lease_contract_length='1yr')
            get_aws_rsv_prices(od, uar, 'No Upfront', 'Hrs',
                               'reserved_1yr_noupfront_shared_low',
                               'reserved_1yr_noupfront_shared_high')
            get_aws_rsv_prices(od, uar, 'All Upfront', 'Quantity',
                               'reserved_1yr_upfront_shared_low',
                               'reserved_1yr_upfront_shared_high')

            get_aws_rsv_prices(od, uar, 'Partial Upfront', 'Quantity',
                               'reserved_1yr_partial_shared_low',
                               'reserved_1yr_partial_shared_high')
            get_aws_rsv_prices(od, uar, 'Partial Upfront', 'Hrs',
                               'reserved_1yr_partial_hr_shared_low',
                               'reserved_1yr_partial_hr_shared_high')

            # Reserved 1yr, Dedidated
            od = name_q.filter(term_type='Reserved',
                               tenancy='Dedicated',
                               lease_contract_length='1yr')
            get_aws_rsv_prices(od, uar, 'No Upfront', 'Hrs',
                               'reserved_1yr_noupfront_dedicated_low',
                               'reserved_1yr_noupfront_dedicated_high')
            get_aws_rsv_prices(od, uar, 'All Upfront', 'Quantity',
                               'reserved_1yr_upfront_dedicated_low',
                               'reserved_1yr_upfront_dedicated_high')

            get_aws_rsv_prices(od, uar, 'Partial Upfront', 'Quantity',
                               'reserved_1yr_partial_dedicated_low',
                               'reserved_1yr_partial_dedicated_high')
            get_aws_rsv_prices(od, uar, 'Partial Upfront', 'Hrs',
                               'reserved_1yr_partial_hr_dedicated_low',
                               'reserved_1yr_partial_hr_dedicated_high')

            # Reserved 3yr, Shared
            od = name_q.filter(term_type='Reserved',
                               tenancy='Shared',
                               lease_contract_length='3yr')
            get_aws_rsv_prices(od, uar, 'No Upfront', 'Hrs',
                               'reserved_3yr_noupfront_shared_low',
                               'reserved_3yr_noupfront_shared_high')
            get_aws_rsv_prices(od, uar, 'All Upfront', 'Quantity',
                               'reserved_3yr_upfront_shared_low',
                               'reserved_3yr_upfront_shared_high')

            get_aws_rsv_prices(od, uar, 'Partial Upfront', 'Quantity',
                               'reserved_3yr_partial_shared_low',
                               'reserved_3yr_partial_shared_high')
            get_aws_rsv_prices(od, uar, 'Partial Upfront', 'Hrs',
                               'reserved_3yr_partial_hr_shared_low',
                               'reserved_3yr_partial_hr_shared_high')

            # Reserved 3yr, Dedidated
            od = name_q.filter(term_type='Reserved',
                               tenancy='Dedicated',
                               lease_contract_length='3yr')
            get_aws_rsv_prices(od, uar, 'No Upfront', 'Hrs',
                               'reserved_3yr_noupfront_dedicated_low',
                               'reserved_3yr_noupfront_dedicated_high')
            get_aws_rsv_prices(od, uar, 'All Upfront', 'Quantity',
                               'reserved_3yr_upfront_dedicated_low',
                               'reserved_3yr_upfront_dedicated_high')

            get_aws_rsv_prices(od, uar, 'Partial Upfront', 'Quantity',
                               'reserved_3yr_partial_dedicated_low',
                               'reserved_3yr_partial_dedicated_high')
            get_aws_rsv_prices(od, uar, 'Partial Upfront', 'Hrs',
                               'reserved_3yr_partial_hr_dedicated_low',
                               'reserved_3yr_partial_hr_dedicated_high')

            uar.save()
