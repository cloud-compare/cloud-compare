# model.py extension to populate the database fron the GCP (Google)

# Some interesting queries:
# Get all instance types:
#  select * from pricing_gcppricing where ptype = 'COMPUTEENGINE' and psubtype = 'VMIMAGE'

import os
import httplib
import json
import re
import zlib

from django.core.management.base import BaseCommand
from pricing.models import GCP

# default site for pricing data
PRICE_URL = 'cloudpricingcalculator.appspot.com'

# default path for pricing index
OFFER_LIST = '/static/data/pricelist.json'

# Converts CamelCase to underbars with pre-compiled re's
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def convert_cc(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


class Command(BaseCommand):
    args = ''
    help = 'Populates pricing database from GCP (Google)'

    def handle(self, *args, **options):

        # Open connection to AWS pricing
        conn = httplib.HTTPConnection(PRICE_URL)

        # get root index
        conn.request('GET', OFFER_LIST)
        res = conn.getresponse()
        if res.status != httplib.OK:
          print 'root index: unexpected status %d' % (res.status)
          return None

        roots = res.read()

        # Get content encoding from header. decode is gzip
        enc = res.getheader('content-encoding', 'text');
        if enc == 'gzip':
            roots = zlib.decompress(roots, 16+zlib.MAX_WBITS)

        # should be JSON, attempt decode
        js = None
        try:
            js = json.loads(roots)
        except:
            return None

        # first level tags:
        # version: Version of file
        #  comment
        #  gcp_price_list 
        #  updated <date>
        #  version
        #print js['comment']
        #print js['updated']
        #print js['version']

	# Combined product and price list.
        prices = js['gcp_price_list']
        for k in prices.keys():
           v = prices[k]

           if re.search('CP-.+', k):
               # 'CP-' names are dash('-') separated names for the product 
               # type and variation. For example 
               #   'CP-COMPUTEENGINE-VMIMAGE-F1-MICRO'
               klist = k.split('-', 3)

               # We know there is at least 1 split since we match 'CP_.+'
               ptype = klist[1]
               psubtype = None
               if len(klist) > 2:
                  psubtype = klist[2]

               pargs = None
               if len(klist) > 3:
                   pargs = klist[3]

               # special case for VMIMAGE
               preemptible = False
               if psubtype == 'VMIMAGE':
                   # is this premptable?
                   if re.match('.+-PREEMPTIBLE', pargs):
                       preemptible = True
                       pargs = pargs.rsplit('-', 1)[0]


               pr = GCP(ptype = ptype, psubtype = psubtype, pargs = pargs,
                              preemptible = preemptible)

               # copy over the first level contents
               for kk in v:
                   # Clean up fields here
                   vv = v[kk]
                   if kk == 'cores' and vv == 'shared':
                       vv = 0
                   print ptype, pargs, kk, vv
                   setattr(pr, kk, vv)
               pr.save()
               

               #print k
               # klist[0]='CP', klist[1]="Product Type", klit[2]=<the rest>
               # Prodcut Types (on 7/28/2016)
               # APP[-ENGINE]
               if ptype == 'APP':
                   pass

               # BIGQUERY
               elif ptype == 'BIGQUERY':
                   pass

               # BIGSTORE
               elif ptype == 'BIGSTORE':
                   pass

               # BIGTABLE
               elif ptype == 'BIGTABLE':
                   pass

               # CLOUD
               elif ptype == 'CLOUD':
                   pass

               # CLOUDCDN
               elif ptype == 'CLOUDCDN':
                   pass

               # CLOUDSQL
               elif ptype == 'CLOUDSQL':
                   pass

               # COMPUTEENGINE - roughly AWS Instances
               elif ptype == 'COMPUTEENGINE':
                   pass

               # CONTAINER
               elif ptype == 'CONTAINER':
                   pass

               # DATAFLOW
               elif ptype == 'DATAFLOW':
                   pass

               # DATAPROC - 'PS-DATAPROC' is complete
               elif ptype == 'DATAPROC':
                   pass

               # DB
               elif ptype == 'DB':
                   pass

               # GENOMICS
               elif ptype == 'GENOMICS':
                   pass

               # NEARLINE
               elif ptype == 'NEARLINE':
                   pass

               # PREDICTION
               elif ptype == 'PREDICTION':
                   pass

               # PUB
               elif ptype == 'PUB':
                   pass

               # STACKDRIVER
               elif ptype == 'STACKDRIVER':
                   pass

               # SUPPORT
               elif ptype == 'SUPPORT':
                   pass

               # TRANSLATE
               elif ptype == 'TRANSLATE':
                   pass

               # VISION
               elif ptype == 'VISION':
                   pass

               else:
                   print "WARNING unrecognized ptype %s" % (ptype)


           else:
               print k, js['gcp_price_list'][k]
               pass
