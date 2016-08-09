
# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.db.models import Count

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

    types = pr.values('ptype').distinct()
    total_types = types.count()

    subtypes = pr.values('psubtype').distinct()
    total_subtypes = subtypes.count();
    product = pr.values('ptype', 'psubtype').order_by('ptype', 'psubtype').distinct()

    args = { 'product' : product,
             'types' : types,
             'subtypes' : subtypes,
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
    offer_name_count = pr.values('offer_code').distinct().count()
    product_family_count = pr.values('product_family').distinct().count()

    pr = pr.values('offer_code', 'product_family').annotate(Count('id'))
    pr = pr.order_by('offer_code', 'product_family')
    prod_variations = pr.distinct().count()

    # Get distinct offer_code values
    on = pr.values('offer_code').distinct().order_by('offer_code')
    offers = []
    for o in on:
        print 'offer=', o
        offers.append(o['offer_code'])

    # get distinct product_family values
    fn = pr.values('product_family').distinct().order_by('product_family')
    pfamilies = []
    for f in fn:
        pfamilies.append(f['product_family'])

    pf = pr.values('product_family').distinct().order_by('product_family')

    # Build a 2-level python dict to lookup [offer_code][product_family]
    # We'll use this to build the table content for rendering
    odict = {}
    for p in pr:
        ok = p['offer_code']
        if not ok in odict:
            odict[ok] = {}

        pk = p['product_family']
        if not pk in odict[ok]:
           odict[ok][pk] = p['id__count']
           print ok, pk, odict[ok][pk]

    tab = []
    for p in pfamilies:
        row = []
        row.append({'label' : p})
        for o in offers:
            if p in odict[o]:
                row.append({'label': '_Y_', 'offer' : o, 'family' : p, 'count' : odict[o][p]})
            else:
                row.append({'label': '_N_'})

        tab.append(row)

#    for f in pf:
#        pfam = pr.filter(product_family = f['product_family'])
#        for o in on:
#            s = pfam.filter(offer_code = o['offer_code'])
#            if s.count() > 0:
#                print o['offer_code'], f['product_family'], s.count()

    args = { 'products' : pr,
             'attrs' : attr,
             'offer_names' : on,
             'offer_name_count' : offer_name_count,
             'product_family_count' : product_family_count,
             'prod_variations' : prod_variations,
             'odict' : odict,
             'table' : tab,
             'product_families' : pf}

    return render(request, 'aws_all.html', args)


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

