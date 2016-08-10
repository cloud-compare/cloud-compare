# Ingests data from a scrape staging directory into the database

# Standard python libraies
import os
import httplib
import zlib
import json
import time
import re

# djnago stuff
from django.core.management.base import BaseCommand, CommandError

# Our models
from pricing.models import AWS, GCP

##### Utility Functions #####

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

##### Amazon AWS Ingest #####

# At this point we have:
#   'offerTermCode'
#   'sku'
#   'effectiveDate'
#   'priceDimensions'
#   'termAttributes'
def ingest_AWS_term_ent(offer_code, term_type, offer_ent, products):

    sku = offer_ent['sku']
    effective_date = offer_ent['effectiveDate']
    price_dimensions = offer_ent['priceDimensions']
    term_attributes = offer_ent['termAttributes']
    prod = products[sku]

    try:
        for p in offer_ent['priceDimensions'].keys():
            # TBD #### Make Create the AWS model entry
            tr = AWS(sku = sku, term_type = term_type, offer_code = offer_code,
                     product_family = prod['productFamily'],
                     effective_date = effective_date)

            # Pick up termAttributes
            for tk in term_attributes.keys():
                setattr(tr, convert_cc(tk), term_attributes[tk])

            # Pick up pricing dimensions
            for pdk in offer_ent.keys():
                pdv = offer_ent[pdk]
                if pdv == 'pricePerUnit':
                    pdv = pdv['USD']

                setattr(tr, convert_cc(pdk), pdv)

            # build product attribute columns
            pattr = prod['attributes']
            for pak in pattr:
                tv = pattr[pak]
                if pak == 'memory':
                    # Cleanup memory: in file 'XXX Gib'. Strip last 4 chars
                    tv = tv[:-4]
                    # replace commas
                    tv = re.sub(',', '', tv)

                setattr(tr, convert_cc(pak), tv)
      
            # Write record to AWS table
            tr.save()

    except:
        print 'Ignore bad entry - sku=%s code=%s type=%s date=%s' % \
              (sku, offer_code, term_type, effective_date)

    return


# Ingest a term list at the level of 'OnDemand' or 'Reserved'
def ingest_AWS_term(offer_code, term_type, offer, products):

    print 'Ingest %s %s' % (offer_code, term_type)

    for o in offer:
        for oo in offer[o]:
            ingest_AWS_term_ent(offer_code, term_type, offer[o][oo], products)

    return


# Ingest a single AWS offer file
def ingest_AWS_offer(offer, opath):

    # build in memory map of product entries mapped by sku
    products = {}
    for sku in offer['products']:
        products[sku] = offer['products'][sku]

    # loop through the terms
    for term_type in offer['terms']:
        ingest_AWS_term(offer['offerCode'], term_type,
                        offer['terms'][term_type], products)

    return


def ingestAmazon(dir, fname):
    print 
    print 'Amazon(AWS) Price List'

    path = '%s%s' % (dir, fname)

    # Read the top level file
    f = open(path, 'r')
    try:
        ijs = json.load(f)
    except:
        raise CommandError('%s is not JSON' % path)
    f.close()

    print 'Publication Date: %s' % ijs['publicationDate']

    for i in ijs['offers']:
        # Split up the entry
        offer =  ijs['offers'][i]
        offer_code = offer['offerCode']
        current = path2name(offer['currentVersionUrl'])
        history = path2name(offer['versionIndexUrl'])

        # read in the offer file
        opath = '%s%s' % (dir, current)
        of = open(opath, 'r')
        try:
            ojs = json.load(of)
        except:
            raise CommandError('offer file %s is not JSON' % opath)
        of.close()

        # ingest the offer
        ingest_AWS_offer(ojs, opath)

    return

##### Google GCP Ingest #####

def ingestGoogle(dir, fname):

    print 
    print 'Google(GCP) Price List'

    path = '%s%s' % (dir, fname)

    # Read the top level file
    f = open(path, 'r')
    try:
        ijs = json.load(f)
    except:
        raise CommandError('%s is not JSON' % path)
    f.close()

    print 'Version:', ijs['version']
    print 'Updated:', ijs['updated']

    prices = ijs['gcp_price_list']
    for pk in prices.keys():
        pv = prices[pk]

        if re.search('CP-.+', pk):
            pkl = pk.split('-', 3)

            # pick up main type
            ptype = pkl[1]

            # pick up subtype if it exists
            psubtype = None
            if len(pkl) > 2:
                psubtype = pkl[2]

            # pick up pargs if they exist
            pargs = None
            if len(pkl) > 3:
                pargs = pkl[3]

            # special case for VMIMAGE's
            preemptible = False
            if psubtype == 'VMIMAGE':
                if re.match('.+-PREEMPTIBLE', pargs):
                    preemptible = True
                    pargs = pargs.rsplit('-', 1)[0]

            pr = GCP(ptype = ptype, psubtype = psubtype, pargs = pargs,
                     preemptible = preemptible)

            # copy over the first level contents
            for kk in pv:
                # Clean up fields here
                vv = pv[kk]
                if kk == 'cores' and vv == 'shared':
                    vv = 0

                setattr(pr, kk, vv)

            # Write out record
            pr.save()

            pass

        else:
            print 'skip %s' % (pk)
            pass


class Command(BaseCommand):
    help = 'Ingests scraped data into databse'

    def add_arguments(self, parser):
        parser.add_argument("directory", nargs = 1,
                            help = 'Directory that contains scraped data')
        parser.add_argument('-m', '--meta', required = False, action = 'store_true',
                            help = 'Print metadata')

    def handle(self, *args, **options):
        directory = options['directory'][0]

        # validate directory
        if not os.path.exists(directory):
            raise CommandError('%s does not exist' % (directory))

        if not os.path.isdir(directory):
            raise CommandError('%s is not a directory' % (directory))

        # validate meta file
        meta = '%s/META' % directory
        if not os.path.exists(meta):
            raise CommandError('%s does not exist' % (meta))

        if not os.path.isfile(meta):
            raise CommandError('%s is not a file' % (meta))

        # read the metadata file
        mf = open(meta, 'r')
        mjs = None
        try:
            mjs = json.load(mf)
        except:
            raise CommandError('%s does not contain JSON' % meta)
        mf.close()

        # validate META file contents
        if not 'cloudProvider' in mjs:
            raise CommandError('%s does not contain "cloudProvider" tag' % meta)
        if not 'host' in mjs:
            raise CommandError('%s does not contain "host" tag' % meta)
        if not 'path' in mjs:
            raise CommandError('%s does not contain "path" tag' % meta)
        if not 'time' in mjs:
            raise CommandError('%s does not contain "time" tag' % meta)

        print 'Scrape Time: %s' % mjs['time']
        print 'Provider:    %s' % mjs['cloudProvider']
        print 'Host:        %s' % mjs['host']
        print 'Path:        %s' % mjs['path']

        # Just dump metadata?
        if options['meta']:
            return;

        # base json file name
        basepath = '%s%s' % (directory, path2name(mjs['path']))
        if not os.path.isfile(basepath):
            raise CommandError('base file %s does not exist' % basepath)

        # Read the base JSON file
        bf = open(basepath, 'r')

        try:
            bjs = json.load(bf)
        except:
            raise CommandError('base file %s is not JSON' % basepath)

        bf.close()

        # break out to the proper ingest handler
        if mjs['cloudProvider'] == 'Amazon':
            ingestAmazon(directory, path2name(mjs['path']))

        elif mjs['cloudProvider'] == 'Google':
            ingestGoogle(directory, path2name(mjs['path']))

        else:
            raise CommandError('No not recognize provider %s' % mjs['cloudProvider'])
