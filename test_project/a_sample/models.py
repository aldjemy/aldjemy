from sample.models import Book


class BookProxy(Book):
    class Meta:
        proxy = True
