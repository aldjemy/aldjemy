import django
from django.contrib.postgres.fields import ArrayField, DateRangeField, JSONField
from django.db import models
from django.utils import timezone


class TicTacToeBoard(models.Model):
    board = ArrayField(models.TextField(), size=9)


class JsonModel(models.Model):
    value = JSONField() if django.VERSION < (3, 1) else models.JSONField()


class DateRangeModel(models.Model):
    date_range = DateRangeField()


class EmailAddress(models.Model):
    created = models.DateTimeField(default=timezone.now, verbose_name='Created')
    user = models.ForeignKey('TicTacToeBoard', models.CASCADE, related_name='email_addresses', verbose_name='User')
    domain = models.CharField(max_length=254, verbose_name='Domain')
    email = models.EmailField(unique=True, verbose_name='Email')
    primary = models.BooleanField(default=False, verbose_name='Primary')
