"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from sample.models import G


class SimpleTest(TestCase):
    def test_aldjemy_initialization(self):
        self.assertTrue(G.sa)
