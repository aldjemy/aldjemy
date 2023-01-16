from django.contrib.postgres.fields import ArrayField, DateRangeField
from django.db import models


class TicTacToeBoard(models.Model):
    board = ArrayField(models.TextField(), size=9)


class JsonModel(models.Model):
    value = models.JSONField()


class DateRangeModel(models.Model):
    date_range = DateRangeField()
