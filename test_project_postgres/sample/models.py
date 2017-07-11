from django.db import models
from django.contrib.postgres.fields import ArrayField


class TicTacToeBoard(models.Model):
    board = ArrayField(models.TextField(), size=9)
