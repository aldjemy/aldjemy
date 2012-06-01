from django.db import models as m

# Create your models here.

class G(m.Model):
    a = m.CharField(max_length="200")


class M(m.Model):
    a = m.CharField(max_length="200")
    b = m.TextField()

    g = m.ManyToManyField(G, related_name='cc_lprojects')

class MN(M):
    c = m.TextField()
