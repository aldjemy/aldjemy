import sys
if sys.version_info[0] == 3:
    unicode = str

from django.test import TestCase
from sample.models import (
        PointGeometry, PointGeography, LineStringGeometry,
        LineStringGeography)


class SimpleTest(TestCase):
    def test_aldjemy_initialization(self):
        self.assertTrue(PointGeometry.sa)
        self.assertTrue(PointGeography.sa)
        self.assertTrue(LineStringGeometry.sa)
        self.assertTrue(LineStringGeography.sa)
    
    def test_querying(self):
        pass
