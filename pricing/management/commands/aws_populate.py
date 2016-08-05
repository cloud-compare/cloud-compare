# model.py extension to populate the database fron the AWS

import os
import httplib
import json
import re

from django.core.management.base import BaseCommand
from pricing.models import AWS

# default site for pricing data
PRICE_URL = 'pricing.us-east-1.amazonaws.com'

# default path for pricing index
OFFER_LIST = '/offers/v1.0/aws/index.json'

# Converts CamelCase to underbars with pre-compiled re's
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def convert_cc(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


class Command(BaseCommand):
    args = ''
    help = 'Populates pricing database from AWS'

    def handle(self, *args, **options):
        # Open connection to AWS pricing
        conn = httplib.HTTPSConnection(PRICE_URL)

        # get root index
        conn.request('GET', OFFER_LIST)

        res = conn.getresponse()

        if res.status != httplib.OK:
          print 'root index: unexpected status %d' % (res.status)
          return None
        roots = res.read()
        conn.close()

        js = json.loads(roots)
        offers = js['offers']
        for k in offers.keys():
            print k

            conn = httplib.HTTPSConnection(PRICE_URL)
            prod_sku = {}
            # Get current pricing info
            curpath = offers[k]['currentVersionUrl']
            conn.request('GET', curpath)
            res = None
            try:
                res = conn.getresponse()
            except:
                continue

            if res.status != httplib.OK:
              continue

            curs = res.read()
            current = json.loads(curs)

            conn.close()

            # cache product by sku dict
            prods = current['products']
            for kk in prods.keys():
                prod_sku[kk] = prods[kk]

            # build merged records
            terms = current['terms']
            for tk in terms.keys():
                for tkk in terms[tk].keys():

                    for tkkk in terms[tk][tkk].keys():
                        # at the level build Terms row
                        t = terms[tk][tkk][tkkk]
                        # create with fixed fields
                        pd = t['priceDimensions']
                        ta = t['termAttributes']

                        # Get cached product record
                        psku = prod_sku[t['sku']]

                        for pdk in pd.keys():
                            tr = AWS(sku = t['sku'], term_type = tk,
                                     offer_code = k,
                                     product_family = psku["productFamily"],
                                     offer_term_code = t['offerTermCode'],
                                     effective_date = t['effectiveDate'])

                            # pick up any term attributes
                            for tak in ta.keys():
                                setattr(tr, convert_cc(tak), ta[tak])
                            # do pricing dimensions
                            for pdkk in pd[pdk].keys():
                                pdvv = pd[pdk][pdkk]
                                if pdkk == 'pricePerUnit':
                                    pdvv = pdvv['USD']
                                setattr(tr, convert_cc(pdkk), pdvv)
                      
                            # build product attribute columns
                            attr = psku['attributes']
                            for kkk in attr.keys():
                                if kkk == 'memory':
                                    # Cleanup memory field.
                                    # json: 2 GiB. Convert to float.
                                    tv = attr[kkk][:-4]
                                    # replace commas
                                    tv = re.sub(',', '', tv)
                                    setattr(tr, convert_cc(kkk), tv)
                                else:
                                    setattr(tr, convert_cc(kkk), attr[kkk])

                            tr.save()

            # TBD #### - Do something with historical data
            vidxpath = offers[k]['versionIndexUrl']
