
# Scrapes pricing files from Cloud prover into local system

import logging
import os
import httplib
import zlib
import json
import time


from django.core.management.base import BaseCommand, CommandError

# Slurp a price file from the internet into memory.
# returns raw data (typically JSON)
def get_price_data(host, path): 
    conn = httplib.HTTPSConnection(host)
    # get root index
    conn.request('GET', path)
    res = conn.getresponse()
    if res.status != httplib.OK:
      # TBD #### Logging
      raise CommandError( 'root index: unexpected status %d' % (res.status) )

    # Read in raw data
    roots = res.read()

    # Get content encoding from header. decode is gzip
    enc = res.getheader('content-encoding', 'text');
    if enc == 'gzip':
        roots = zlib.decompress(roots, 16+zlib.MAX_WBITS)

    conn.close()
    return roots


# Host and path for AWS pull
AWS_HOST = 'pricing.us-east-1.amazonaws.com'
AWS_PATH = '/offers/v1.0/aws/index.json'

def pull_aws(dir):
    host = AWS_HOST
    path = AWS_PATH
    data = get_price_data(host, path)

    # should be JSON, attempt decode
    js = None
    try:
        js = json.loads(data)
    except:
        # TBD #### Logging
        pass

    meta = {
               'cloudProvider' : "Amazon",
               'host' : host,
               'path' : path,
               'time' : time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
           }

    # Write data to index
    f = open('%s/%s' % (dir, os.path.basename(path)), "w")
    f.write(data)
    f.close()

    # Loop through offers
    for o in js['offers']:
        od = js['offers'][o]

        data = get_price_data(host, od['currentVersionUrl'])
        f = open('%s/%s.current.json' % (dir, od['offerCode']), "w")
        f.write(data)
        f.close()

        data = get_price_data(host, od['versionIndexUrl'])
        f = open('%s/%s.history.json' % (dir, od['offerCode']), "w")
        f.write(data)
        f.close()


    # Write out metadata
    f = open('%s/META' % (dir), 'w')
    f.write(json.dumps(meta))
    f.close()
    
    pass

GCP_HOST = 'cloudpricingcalculator.appspot.com'
GCP_PATH = '/static/data/pricelist.json'

def pull_gcp(dir):

    host = GCP_HOST
    path = GCP_PATH
    meta = {
               'cloudProvider' : "Google",
               'host' : host,
               'path' : path,
               'time' : time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
           }

    data = get_price_data(host, path)

    # should be JSON, attempt decode
    js = None
    try:
        js = json.loads(data)
    except:
        # TBD #### Logging
        pass

    # Write data into directory
    f = open('%s/%s' % (dir, os.path.basename(path)), 'w')
    f.write(data)
    f.close()

    # Write out metadata
    f = open('%s/META' % (dir), 'w')
    f.write(json.dumps(meta))
    f.close()
    pass


class Command(BaseCommand):
    help = 'Scrapes pricing data from public cloud (AWS or Google) into local files'


    def add_arguments(self, parser):
        parser.add_argument("directory", nargs = 1,
                            help = 'Directory to place scraped data')
        parser.add_argument('--aws', required = False, action = 'store_true',
                            help = 'Scrape data from Amazon AWS')
        parser.add_argument('--gcp', required = False, action = 'store_true',
                            help = 'Scrape data from Google GCP')

    def handle(self, *args, **options):

        # Only one of --aws or --gcp is required
        if options['aws'] == options['gcp']:
            raise CommandError('one (and only one) of --aws or --gcp is required')
            return


        directory = options['directory'][0]

        # make sure the directory exists
        if not os.path.isdir(directory):
            raise CommandError('%s is not a directory' % directory)
            return 1;

        # spool-in aws if needed
        if options['aws']:
            pull_aws(directory)

        # spool-in gcp if needed
        if options['gcp']:
            pull_gcp(directory)

