from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.db.models import Count

from django.db import connection

from pricing.models import AWS, GCP


def build_aws_main():
    items = []

    # Offerings -> Families
    aws = AWS.objects
    aws = aws.values('offer_code', 'product_family')
    pr = aws.order_by('offer_code', 'product_family').distinct()

    # Do a couple of 'favorites'
    fitems = []
    url = '/pricing/aws/offer_code=AmazonEC2/product_family=Compute Instance'
    fitems.append({'label': 'AmazonEC2/Compute Instance', 'items': None,
                  'url': url, 'enabled': True})
    url = '/pricing/aws/offer_code=AmazonS3/product_family=Storage'
    fitems.append({'label': 'AmazonS3/Storage', 'items': None,
                  'url': url, 'enabled': True})

    items.append({'label': 'Favorites', 'items': fitems, 'enabled': True,
                  'expanded': True})

    # Offers and Families
    oitems = []
    loffer = None
    soitems = []
    for p in pr:
        if p['offer_code'] != loffer:
            # append new item to items
            if loffer is not None:
                oitems.append({'label': loffer, 'items': soitems,
                              'enabled': True, 'expanded': False})

            soitems = []
            loffer = p['offer_code']

        # append family to currently building offer
        url = '/pricing/aws/offer_code=%s/product_family=%s' % \
              (loffer, p['product_family'])
        soitems.append({'label': p['product_family'], 'items': None,
                        'url': url, 'enabled': True, 'expanded': False})
        pass

    if len(soitems) > 0:
        oitems.append({'label': loffer, 'items': soitems,
                       'enabled': True, 'expanded': False})

    items.append({'label': 'All Product Offerings', 'items' : oitems,
                  'enabled': True, 'expanded': False})

    # Family -> Offering
    pr = aws.order_by('product_family', 'offer_code').distinct()

    fitems = []
    lfamily = None
    sfitems = []
    for p in pr:
        if p['product_family'] != lfamily:
            if lfamily is not None:
                fitems.append({'label': lfamily, 'items': sfitems,
                               'enabled': True, 'expanded': False})

            sfitems = []
            lfamily = p['product_family']

        url = '/pricing/aws/offer_code=%s/product_family=%s' % \
              (p['offer_code'], lfamily)
        sfitems.append({'label': p['offer_code'], 'items': None,
                        'url': url, 'enabled': True, 'expanded': False})

    # Pick up last item
    if len(sfitems) > 0:
        fitems.append({'label': lfamily, 'items': sfitems,
                       'enabled': True, 'expanded': False})

    items.append({'label': 'All Product Families', 'items' : fitems, 'enabled': True,
                  'expanded': False})

    return items


def build_gcp_main():

    gcp = GCP.objects
    pr = gcp.values('ptype', 'psubtype').order_by('ptype', 'psubtype').distinct()

    # Offers and Families
    items = []
    oitems = []
    loffer = None
    soitems = []
    
    for p in pr:
        print p
        if p['ptype'] != loffer:
            # append new item to items
            if loffer is not None:
                oitems.append({'label': loffer, 'items': soitems,
                              'enabled': True, 'expanded': False})

            soitems = []
            loffer = p['ptype']

        # append family to currently building offer
        url = '/pricing/gcp/ptype=%s/psubtype=%s' % \
              (loffer, p['psubtype'])
        soitems.append({'label': p['psubtype'], 'items': None,
                        'url': url, 'enabled': True, 'expanded': False})
        pass

    if len(soitems) > 0:
        oitems.append({'label': loffer, 'items': soitems,
                       'enabled': True, 'expanded': False})

    items.append({'label': 'All Product Offerings', 'items' : oitems,
                  'enabled': True, 'expanded': False})

    # Families and Offers
    # #### TBD
    pr = gcp.values('psubtype', 'ptype').order_by('psubtype', 'ptype').distinct()

    fitems = []
    lfamily = None
    sfitems = []
    for p in pr:
        if p['psubtype'] != lfamily:
            if lfamily is not None:
                fitems.append({'label': lfamily, 'items': sfitems,
                               'enabled': True, 'expanded': False})

            sfitems = []
            lfamily = p['psubtype']

        url = '/pricing/gcp/ptype=%s/psubtype=%s' % \
              (p['ptype'], lfamily)
        sfitems.append({'label': p['ptype'], 'items': None,
                        'url': url, 'enabled': True, 'expanded': False})

    if len(sfitems) > 0:
        fitems.append({'label': lfamily, 'items': sfitems,
                       'enabled': True, 'expanded': False})

    items.append({'label': 'All Product Families', 'items' : fitems,
                  'enabled': True, 'expanded': False})

    return items


def main(request):
    items = []
 
    # Future - Comparisons
    fmsg = 'This is a future planned feature. It is currently not implemented'
    citem = [{'label': fmsg, 'items': None, 'expanded': True}]

    items.append({'label': 'Compare Cloud Offerings', 'items': citem,
                  'enabled': True, 'expanded': True})

    # Amazon AWS
    items.append({'label': 'Amazon AWS', 'items': build_aws_main(),
                  'enabled': True, 'expanded': True})

    # Amazon GCP
    items.append({'label': 'Google GCP', 'items': build_gcp_main(),
                  'enabled': True, 'expanded': True})

    args = {'body_title': 'Main', 'items': items}
    return render(request, 'bootstrap_main.html', args)

