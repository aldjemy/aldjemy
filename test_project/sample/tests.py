"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from sample.models import Chapter, Book, Author, StaffAuthor, Review
from a_sample.models import BookProxy


class SimpleTest(TestCase):
    def test_aldjemy_initialization(self):
        self.assertTrue(Chapter.sa)
        self.assertTrue(Book.sa)
        self.assertTrue(Author.sa)
        self.assertTrue(StaffAuthor.sa)
        self.assertTrue(Review.sa)
        self.assertTrue(BookProxy.sa)
