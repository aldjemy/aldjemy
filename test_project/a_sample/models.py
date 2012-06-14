from django.db import models as m
from sample.models import G

# Create your models here.

class GP(G):
    class Meta:
    	proxy=True