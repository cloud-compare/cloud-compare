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
        call_command('scrape', '--aws', self.tmpdir)
        self.assertTrue(os.path.isfile('%s/META' % self.tmpdir))

        call_command('ingest', self.tmpdir)
        self.assertNotEqual(AWS.objects.count(), 0)


    # Try Scraping from Google
    def test_gcp(self):
        call_command('scrape', '--gcp', self.tmpdir)
        self.assertTrue(os.path.isfile('%s/META' % self.tmpdir))

        call_command('ingest', self.tmpdir)
        self.assertNotEqual(GCP.objects.count(), 0)
