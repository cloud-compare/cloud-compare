from django.test import TestCase
from django.core.management import call_command

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


    # Try Scraping from Google
    def test_gcp(self):
        call_command('scrape', '--gcp', self.tmpdir)
        self.assertTrue(os.path.isfile('%s/META' % self.tmpdir))
