
# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q

from pricing.models import AWS
from pricing.models import GCP

from forms import EC2InstanceForm

import pprint

def home(request):
    args = {}
    return render(request, "home.html", args)

def index(request):
    return HttpResponse("Future index page")
#
# Views for GCP (Google Cloud Platform)
#
def gcp(request):
    pr = GCP.objects
    total_rows = pr.count()
    total_types = pr.values('ptype').distinct().count();
    total_subtypes = pr.values('psubtype').distinct().count();

    product = pr.values('ptype', 'psubtype').order_by('ptype', 'psubtype').distinct()

    args = { 'product' : product,
             'total_rows' : total_rows,
             'total_types' : total_types,
             'total_subtypes' : total_subtypes}

    return render(request, 'gcp_all.html', args)


def gcp_ptype_psubtype(request, ptype, psubtype):
    print ptype, psubtype

    pr = GCP.objects;
    pr = pr.filter(ptype = ptype, psubtype = psubtype)
    pr = pr.order_by('memory', 'cores', 'preemptible')

    args = {'ptype' : ptype, 'psubtype' : psubtype, 'product' : pr, 'count' : pr.count()}

    template = 'gcp_ptype_psubtype.html'
    if ptype == 'COMPUTEENGINE' and psubtype == 'VMIMAGE':
        template = 'gcp_vmimage.html'

    return render(request, template, args)
    

#
# Views for AWS (Amazon Web Services)
#

# Displays table of offer_code and product_family
def aws(request):
    pr = AWS.objects
    attr = { 'total_rows' : pr.count() }
    attr['total_offer_code'] = pr.values('offer_code').distinct().count()
    attr['total_product_family'] = pr.values('product_family').distinct().count()
    pr = pr.values('offer_code', 'product_family')
    pr = pr.order_by('offer_code', 'product_family')
    pr = pr.distinct()
    attr['prod_variations'] = pr.count()
    return render(request, 'aws_all.html', { 'products' : pr, 'attrs' : attr})


# Displays drill-down to records with the same offer_code and product_family
def aws_prodfamily(request, offer_code, product_family):
    print "lll", offer_code
    pr = AWS.objects
    pr = pr.filter(offer_code = offer_code, product_family = product_family)

    if product_family == 'Bundle':
        pr = pr.order_by('from_location', 'from_location_type', 'to_location',
                         'to_location_type', 'begin_range')
        args = {'offer_code' : offer_code, 'product_family': product_family,
                'products' : pr , 'count' : pr.count()}
        return render(request, 'aws_bundle.html', args)

    # Special case for Data Transfer
    if product_family == 'Data Transfer':
        pr = pr.order_by('from_location', 'from_location_type', 'to_location',
                         'to_location_type', 'begin_range')
        args = {'offer_code' : offer_code, 'product_family': product_family,
                'products' : pr , 'count' : pr.count()}
        return render(request, 'aws_data_transfer.html', args)


    # handle EC2 instances separately.
    # there are something like 35000 of then as of 7/2016, so one 
    # big list won't do. Instead do instance types.
    if product_family == 'Compute Instance':
        pr = pr.order_by('instance_family', 'memory', 'instance_type')
        pr = pr.values('instance_family', 'instance_type', 'vcpu', 'memory',
                       'current_generation', 'physical_processor',
                       'network_performance', 'storage')
        pr = pr.distinct()
     
        args = {'offer_code' : offer_code, 'product_family': product_family, 'products' : pr }
        return render(request, 'aws_compute_instance_list.html', args)

    # Generic offer, family list
    pr = pr.order_by('location')
    args = {'offer_code' : offer_code, 'product_family': product_family,
            'count' : pr.count(), 'products' : pr }

    return render(request, 'aws_offer_family.html', args)

# display a specific EC2 instance type
def aws_compute_instance(request, offer_code, product_family, instance_type):
    print offer_code
    forms = EC2InstanceForm(request.POST or None)

    # Build the basic list
    pr = AWS.objects
    pr = pr.filter(Q(product_family = 'Compute Instance'),
                   Q(instance_type = instance_type))

    # Get summarized information about this instance_type
    sum = pr.values('instance_family', 'instance_type', 'vcpu', 'memory',
                    'physical_processor', 'network_performance', 
                    'storage', 'current_generation', 'clock_speed', 
                    'dedicated_ebs_throughput')
    sum = sum.distinct()

    # This loop dynamically builds a query based on aarguments from the url
    if request.POST:
        print 'BBB', request.POST.items()
        for r in request.POST.lists():
            k, v = r
            if k == 'csrfmiddlewaretoken':
                continue;
            qs = None
            for l in v:
                q = { k : l }
                if qs == None:
                    qs = Q(**q)
                else:
                    qs = qs | Q(**q)
            pr = pr.filter(qs)


    # We want the list ordered by location for display
    pr = pr.order_by('location', 'term_type', 'operating_system', 'lease_contract_length', 'tenancy', 'purchase_option', 'unit')


    print offer_code
    args = {
               'offer_code' : offer_code,
               'product_family' : product_family,
               'instance_type' : instance_type,
               'summary' : sum,
               'products' : pr,
               'pcount' : pr.count(),
               'forms' : forms,
               'path' : request.path,
           }

    return render(request, 'aws_compute_instance.html', args)

