# Ingests data from a scrape staging directory into the database

import os
import httplib
import zlib
import json
import time

from django.core.management.base import BaseCommand, CommandError


# Convert a pathname to a flat file name
# eg. /foo/bar.x -> foo.bar.x
def path2name(path):
    npath = path.replace('/', '.')
    if npath[0] == '.':
        npath = npath[1:]
    return npath


# At this point we have:
#   'offerTermCode'
#   'sku'
#   'effectiveDate'
#   'priceDimensions'
#   'termAttributes'
def ingest_AWS_term_ent(offer_code, term_type, offer_ent, products):

    for p in offer_ent['priceDimensions']:
        # TBD #### Make Create the AWS model entry
        pass

    return


# Ingest a term list at the level of 'OnDemand' or 'Reserved'
def ingest_AWS_term(offer_code, term_type, offer, products):
    print 'ingest_AWS_term', offer_code, term_type
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


def ingestGoogle(dir, fname):
    print 'ingest Google %s%s' % (dir, fname)
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
