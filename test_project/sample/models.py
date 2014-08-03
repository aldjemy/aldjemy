from django.db import models


class Chapter(models.Model):
    title = models.CharField(max_length=200)
    book = models.ForeignKey('Book')


class Book(models.Model):
    title = models.CharField(max_length=200)


class Author(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField()

    books = models.ManyToManyField(Book, related_name='books')


class StaffAuthor(Author):
    role = models.TextField()


class Review(models.Model):
    book = models.ForeignKey('a_sample.BookProxy')


class Log(models.Model):
    _DATABASE = 'logs'

    record = models.CharField(max_length=100)
