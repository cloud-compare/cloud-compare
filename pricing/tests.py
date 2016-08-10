from django.test import TestCase
from django.core.management import call_command

from pricing.models import AWS
from pricing.models import GCP

import os
import tempfile
import shutil

# Tests for management 'scrape' command
class ScrapeTest(TestCase):

    tmpdir = None

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()


    def tearDown(self):
        shutil.rmtree(self.tmpdir)


    # Try Scraping from AWS
    def test_aws(self):
        # scrape AWS
        call_command('scrape', '--aws', self.tmpdir)

        # Ensure META file was created
        self.assertTrue(os.path.isfile('%s/META' % self.tmpdir))

        # ingest
        call_command('ingest', self.tmpdir)

        # Ensure something was created
        self.assertNotEqual(AWS.objects.count(), 0)

        # ensure we have some prices
        self.assertNotEqual(AWS.objects.filter(price_per_unit__gt = 0).count(), 0)


    # Try Scraping from Google
    def test_gcp(self):

        # scrape from Google
        call_command('scrape', '--gcp', self.tmpdir)

        # ensure META file was created
        self.assertTrue(os.path.isfile('%s/META' % self.tmpdir))

        # Ingest it
        call_command('ingest', self.tmpdir)
        self.assertNotEqual(GCP.objects.count(), 0)

        # make sure we have some non-zero prices.
        self.assertNotEqual(GCP.objects.filter(us__gt = 0).count(), 0)
        self.assertNotEqual(GCP.objects.filter(asia__gt = 0).count(), 0)
        self.assertNotEqual(GCP.objects.filter(europe__gt = 0).count(), 0)
