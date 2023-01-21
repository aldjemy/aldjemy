from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from aldjemy.meta import AldjemyMeta


class Group(models.Model):
    """A model with the same name as a Django model to trigger some warnings."""

    # https://github.com/aldjemy/aldjemy/issues/205


class Chapter(models.Model):
    title = models.CharField(max_length=200)
    book = models.ForeignKey("Book", on_delete=models.CASCADE)


class Book(models.Model):
    title = models.CharField(max_length=200)


class ArticleAuthorAssociation(models.Model):
    author = models.ForeignKey(
        "Author", on_delete=models.CASCADE, related_name="article_associations"
    )
    article = models.ForeignKey(
        "Article", on_delete=models.CASCADE, related_name="author_associations"
    )


class Article(models.Model):
    title = models.CharField(max_length=200)


class BookProxy(Book):
    class Meta:
        proxy = True


class Author(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField()
    books = models.ManyToManyField(Book, related_name="books")
    article = models.ManyToManyField(
        Article, through=ArticleAuthorAssociation, related_name="authors"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class StaffAuthor(Author):
    role = models.TextField()
    date = models.DateTimeField()


class StaffAuthorProxy(Author):
    class Meta:
        proxy = True


class Review(models.Model):
    book = models.ForeignKey("BookProxy", on_delete=models.CASCADE)


class Log(models.Model, metaclass=AldjemyMeta):
    _DATABASE = "logs"

    record = models.CharField(max_length=100)

    def __str__(self):
        return self.record

    @property
    def reversed_record(self):
        return self.record[::-1]

    this_is_not_copied = "something"


class Person(models.Model):
    parents = models.ManyToManyField("self", related_name="children")


class MemberCollective(models.Model):
    name = models.CharField(_("name"), max_length=20, null=False, blank=False)


class Membership(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    member_collective = models.ForeignKey(
        "MemberCollective", on_delete=models.CASCADE, related_name="member_memberships"
    )


class Member(models.Model):
    name = models.CharField(_("name"), max_length=255, null=False, blank=False)

    collectives = models.ManyToManyField(
        MemberCollective,
        related_name="members",
        through="Membership",
    )


class Item(models.Model):
    label = models.TextField(null=False, blank=False)
    legacy_id = models.CharField(max_length=255, unique=True, null=False, blank=False)


class RelatedToItemViaPrimaryKey(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)


class RelatedToItemViaUniqueField(models.Model):
    item = models.ForeignKey(Item, to_field="legacy_id", on_delete=models.CASCADE)
