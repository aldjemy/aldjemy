import django
from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


class TicTacToeBoard(models.Model):
    board = ArrayField(models.TextField(), size=9)


class JsonModel(models.Model):
    value = JSONField() if django.VERSION < (3, 1) else models.JSONField()
