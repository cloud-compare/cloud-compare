"""Views on the GCP (Google) Table."""
from django.http import HttpResponse
from django.shortcuts import render

from models import GCP


# Price per month 
# TBD ### Work in GCP discount curve
def gcp_per_year(price_per_hour):
    return price_per_hour * 8760 * 0.7

class VMImageItem:

    def __init__(self, name, memory, cores):
        self.name = name
        self.memory = memory
        self.cores = cores

    def __repr__(self):
        return repr((self.name, self.memory, self.cores,
                    self.us, self.asia, self.europe,
                    self.us_p, self.asia_p, self.europe_p))

    def set_base(self, us, asia, europe):
        self.us = us
        self.asia = asia
        self.europe = europe

    def set_preempt(self, us, asia, europe):
        self.us_p = us
        self.asia_p = asia
        self.europe_p = europe

    def name(self):
        return self.name

    def memory(self):
        return self.memory

    def cores(self):
        return self.cores

    def us(self):
        return self.us

    def asia(self):
        return self.asia

    def europe(self):
        return self.europe

    def us_p(self):
        return self.us

    def asia_p(self):
        return self.asia

    def europe_p(self):
        return self.europe
        


def gcp_vmimage_list(request, ptype, psubtype):

    gcp = GCP.objects.filter(psubtype='VMIMAGE')
    gcp = gcp.order_by('pargs')

    image_d = {}
    for g in gcp:
        image_sp = g.pargs.split('-')
        if len(image_sp) < 2:
            print 'bad image name %s - skip' % g.pargs
            continue

        itype = image_sp[1]

        if itype not in image_d:
            image_d[itype] = {}

        cur_type = image_d[itype]
        if g.pargs not in cur_type:
            cur_type[g.pargs] = VMImageItem(g.pargs, g.memory, g.cores)

        if g.preemptible:
            cur_type[g.pargs].set_preempt(g.us, g.asia, g.europe)
        else:
            cur_type[g.pargs].set_base(g.us, g.asia, g.europe)

    # for each type, sort the sublist by memory
    images = []
    for k in image_d.keys():

        l = []
        for kk in image_d[k]:
            l.append(image_d[k][kk])

        stup = sorted(l, key=lambda vmimageitem: vmimageitem.memory)
        images.append({'type': k, 'images': stup})

    items = []
    for g in gcp:
        items.append({
                       'label': g.pargs,
                       'memory': g.memory,
                       'cores': g.cores,
                       'us_price': g.us,
                       'asia_price': g.asia,
                       'europe_price': g.europe,
                       'preemptible': g.preemptible,
                     })

    args = {
             'offer_code': ptype,
             'product_family': psubtype,
              'items' : items,
              'images': images,
           }

    return render(request, 'bootstrap_gcp_vmimage_list.html', args)


def gcp_ptype_psubtype(request, ptype, psubtype):
    if psubtype == 'VMIMAGE':
        return gcp_vmimage_list(request, ptype, psubtype)

    return HttpResponse(status=404)


def gcp_vmimage(request, image):

    gcp = GCP.objects.filter(pargs=image)
    memory = gcp[0].memory
    cores = gcp[0].cores
    core_type = 'Dedicated'
    if (cores == 0):
        core = 1
        core_type = 'Shared'

    specs = {
              'memory': memory,
              'cores': cores,
              'core_type': core_type
            }

    # Get per hour prices
    base = gcp.get(preemptible=False)
    base_p = {
               'us': {
                       'per_hour': base.us,
                       'per_year': gcp_per_year(base.us)
                     },
               'asia': {
                        'per_hour': base.asia,
                        'per_year': gcp_per_year(base.asia)
                       },
               'europe': {
                         'per_hour': base.europe,
                         'per_year': gcp_per_year(base.europe)
                      },
             }

    # Per anything larger than an hour makes no sense for preemptible
    preempt = gcp.get(preemptible=True)
    preempt_p = {
               'us': {
                       'per_hour': preempt.us,
                     },
               'asia': {
                        'per_hour': preempt.asia,
                       },
               'europe': {
                         'per_hour': preempt.europe,
                      },
             }

    prices = {
               'base': base_p,
               'preempt': preempt_p,
             }

    args = {
             'offer_code': 'VMIMAGE',
             'product_family': image,
             'specs': specs,
             'prices': prices,
           }
    return render(request, 'bootstrap_gcp_vmimage.html', args)
