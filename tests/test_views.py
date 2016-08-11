from django.test import TestCase
from django.core.management import call_command

from pricing.models import AWS
from pricing.models import GCP

import os
import tempfile
import shutil


class DBTest(TestCase):

    fixtures = ['test_db.json']

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test1(self):
        # make sure AWS table has data
        self.assertNotEqual(AWS.objects.count(), 0)

        # make sure GCP table has data
        self.assertNotEqual(GCP.objects.count(), 0)
