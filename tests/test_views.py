from django.test import TestCase, Client
from django.core.management import call_command

from pricing.models import AWS
from pricing.models import GCP

import os
import tempfile
import shutil


class ViewTest(TestCase):

    # small chunk of database
    fixtures = ['test_db.json']

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_db(self):
        # make sure AWS table has data
        self.assertNotEqual(AWS.objects.count(), 0)

        # make sure GCP table has data
        self.assertNotEqual(GCP.objects.count(), 0)

    def test_root(self):
        # make sure we can set to root
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)

        # try a bogus url, should get 200 with error page
        response = c.get('/bad-url')
        self.assertEqual(response.status_code, 200)

    def test_pricing(self):
        pass
