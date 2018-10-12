from django.conf import settings
from django.contrib.gis.db import models
from aldjemy.meta import AldjemyMeta

SRID = 4326 # global spatial reference system

class PointGeography(models.Model, metaclass=AldjemyMeta):
    location = models.PointField(
        geography=True,
        srid=SRID
    )


class LineStringiGeography(models.Model, metaclass=AldjemyMeta):
    location = models.LineStringField(
        geography=True,
        srid=SRID
    )


class PointGeometry(models.Model, metaclass=AldjemyMeta):
    location = models.PointField(
        geography=False,
        srid=SRID
    )


class LineStringGeometry(models.Model, metaclass=AldjemyMeta):
    location = models.LineStringField(
        geography=False,
        srid=SRID
    )

