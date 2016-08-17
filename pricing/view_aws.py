"""Views on the AWS Table."""
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.db.models import Count
from django.db.models import Min, Max

from pricing.models import AWS


# Displays a AWS 'Bundle' product_family
def aws_family_bundle(request, offer_code):
    """Handle AWS 'Bundle' items."""
    aws = AWS.objects
    aws = aws.filter(offer_code=offer_code,
                     product_family='Bundle')

    pr = aws.order_by('from_location', 'from_location_type', 'to_location',
                         'to_location_type', 'begin_range')
    args = {'offer_code': offer_code, 'product_family': 'Bundle',
            'products': pr, 'count': pr.count()}
    return render(request, 'bootstrap_aws_bundle.html', args)



def aws_family_data_transfer(request, offer_code):
    """Handle AWS 'Data Transfer' items."""
    aws = AWS.objects
    aws = aws.filter(offer_code=offer_code,
                     product_family='Data Transfer')

    # pr = aws.order_by('from_location', 'from_location_type', 'to_location',
    #                  'to_location_type', 'begin_range')
    pr = aws.order_by('from_location', 'to_location', 'transfer_type',
                      'begin_range')

    items = []
    ttlist = pr.values('transfer_type').order_by('transfer_type').distinct()
    for tt in ttlist:
        print tt['transfer_type']
        ttpr = aws.filter(transfer_type=tt['transfer_type'])
        min_price = ttpr.aggregate(Min('price_per_unit'))
        max_price = ttpr.aggregate(Max('price_per_unit'))
        items.append({
                     'label': tt['transfer_type'],
                     'min_price': min_price['price_per_unit__min'],
                     'max_price': max_price['price_per_unit__max'],
                     })

        

    dpr = pr.values('transfer_type', 'price_per_unit', 'unit')
    dpr = dpr.order_by('transfer_type')
    dpr = dpr.annotate(Max('price_per_unit')).annotate(Min('price_per_unit'))
    dpr = dpr.distinct()

    args = {'offer_code': offer_code, 'product_family': 'Data Transfer',
            'items': items,
            'products': dpr, 'count': pr.count()}
    return render(request, 'bootstrap_aws_data_transfer.html', args)


def aws_family_compute_instance(request, offer_code):
    """Handle AWS 'Compute Instance' items."""
    aws = AWS.objects
    aws = aws.filter(offer_code=offer_code,
                     product_family='Compute Instance',
                     term_type = 'OnDemand', price_per_unit__gt = 0)
    pr = aws.order_by('instance_family', 'memory', 'instance_type')
    pr = pr.values('instance_family', 'instance_type', 'vcpu', 'memory',
                   'current_generation', 'physical_processor',
                   'network_performance', 'storage')
    pr = pr.distinct()

    nregions = aws.values('location').order_by('location').distinct().count()

    # Build tree structure
    items = []
    sitems = []
    ifamily = None
    for p in pr:
       if p['instance_family'] != ifamily:
           if ifamily is not None:
               items.append({'label': ifamily, 'items': sitems})

           ifamily = p['instance_family']
           sitems = []

       iregions = aws.filter(instance_type=p['instance_type']). \
                  values('instance_type', 'location'). \
                  order_by('filter').distinct().count()

       print p['instance_type'], iregions, nregions

       sitems.append({'item' : p, 'all_regions': (iregions == nregions)})
       pass

    if len(sitems) > 0:
        items.append({'label': ifamily, 'items': sitems})

    args = {'offer_code': offer_code,
            'product_family': 'Compute Instance',
            'items': items,
            'products': pr}
    return render(request, 'bootstrap_aws_compute_instance_l1.html', args)


def aws_family_storage(request, offer_code):
    """Handle AWS 'Storage' items."""
    # Generic handling for other combos
    aws = AWS.objects
    aws = aws.filter(offer_code=offer_code, product_family='Storage')

    vlist = []
    vtpr = aws.values('volume_type').order_by('volume_type').distinct()
    for vt in vtpr:
        print vt['volume_type']
        a = aws.filter(volume_type=vt['volume_type'])
        vlist.append({'label': vt['volume_type'], 'products': a})

    args = {'offer_code': offer_code, 'product_family': 'Storage',
            'items': vlist}

    return render(request, 'bootstrap_aws_storage.html', args)


def aws_offer_family(request, offer_code, product_family):
    """Handle AWS requests where offer_code and product_family are known."""

    # Some special cases first.
    # Bundle
    if product_family == 'Bundle':
        return aws_family_bundle(request, offer_code)

    # Data Transfer
    if product_family == 'Data Transfer':
        return aws_family_data_transfer(request, offer_code)

    # Compute Instance
    if product_family == 'Compute Instance':
        return aws_family_compute_instance(request, offer_code)

    # Storage
    if product_family == 'Storage':
        return aws_family_storage(request, offer_code)

    # Generic handling for other combos
    aws = AWS.objects
    aws = aws.filter(offer_code=offer_code, product_family=product_family)

    pr = aws.order_by('location')
    args = {'offer_code': offer_code, 'product_family': product_family,
            'count': pr.count(), 'products': pr}

    return render(request, 'bootstrap_aws_offer_family.html', args)


# Information for a specific instance type (eg. 't2.micro')
def aws_compute_instance(request, offer_code, product_family, instance_type):
    """Handle AWS requests for a specific compute_instance."""

    aws = AWS.objects.filter(Q(product_family='Compute Instance'),
                     Q(instance_type=instance_type))

    # Get summarized information about this instance_type
    sum = aws.values('instance_family', 'instance_type', 'vcpu', 'memory',
                     'physical_processor', 'network_performance',
                     'storage', 'current_generation', 'clock_speed',
                     'dedicated_ebs_throughput')
    sum = sum.distinct()

    # TBD #### Pricing data
    args = {
               'offer_code': offer_code,
               'product_family': product_family,
               'instance_type': instance_type,
               'instance': sum[0],
           }
    return render(request, 'bootstrap_aws_compute_instance.html', args)
