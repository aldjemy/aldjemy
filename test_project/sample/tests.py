from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TestCase
from sqlalchemy import MetaData
from sqlalchemy.orm import aliased

from aldjemy.core import Cache, get_connection_string, get_engine
from aldjemy.orm import construct_models
from aldjemy.session import get_session
from test_project.sample.models import (
    Author,
    Book,
    BookProxy,
    Chapter,
    Item,
    Log,
    Person,
    RelatedToItemViaPrimaryKey,
    RelatedToItemViaUniqueField,
    Review,
    StaffAuthor,
    StaffAuthorProxy,
)

User = get_user_model()


class SimpleTest(TestCase):
    def test_aldjemy_initialization(self):
        self.assertTrue(Chapter.sa)
        self.assertTrue(Book.sa)
        self.assertTrue(Author.sa)
        self.assertTrue(StaffAuthor.sa)
        self.assertTrue(StaffAuthorProxy.sa)
        self.assertTrue(Review.sa)
        self.assertTrue(BookProxy.sa)
        self.assertTrue(User.sa)

        # Automatic Many to Many fields get the ``sa`` property
        books_field = Author._meta.get_field("books")
        self.assertTrue(books_field.remote_field.through.sa)

    def test_engine_override_test(self):
        self.assertEqual(get_connection_string(), "sqlite+pysqlite://")

    def test_querying(self):
        Book.objects.create(title="book title")
        Book.objects.all()
        self.assertEqual(Book.sa.query().count(), 1)

    def test_user_model(self):
        u = User.objects.create()
        Author.objects.create(user=u)
        a = Author.sa.query().first()
        self.assertEqual(a.user.id, u.id)


class AliasesTest(TestCase):
    databases = "__all__"

    def test_engines_cache(self):
        self.assertEqual(get_engine("default"), Cache.engines["default"])
        self.assertEqual(get_engine("logs"), Cache.engines["logs"])
        self.assertEqual(get_engine(), Cache.engines["default"])
        self.assertNotEqual(get_engine("default"), get_engine("logs"))

    def test_sessions(self):
        session_default = get_session()
        session_default2 = get_session("default")
        self.assertEqual(session_default, session_default2)
        session_logs = get_session("logs")
        self.assertEqual(connections["default"].sa_session, session_default)
        self.assertEqual(connections["logs"].sa_session, session_logs)
        self.assertNotEqual(session_default, session_logs)

    def test_logs(self):
        Log.objects.create(record="1")
        Log.objects.create(record="2")
        self.assertEqual(Log.objects.using("logs").count(), 2)
        self.assertEqual(Log.sa.query().count(), 2)
        self.assertEqual(Log.sa.query().all()[0].record, "1")


class AldjemyMetaTests(TestCase):
    databases = "__all__"

    def test_meta(self):
        Log.objects.create(record="foo")

        foo = Log.sa.query().one()
        self.assertEqual(str(foo), "foo")
        self.assertEqual(foo.reversed_record, "oof")
        self.assertFalse(hasattr(foo, "this_is_not_copied"))


class CustomMetaDataTests(TestCase):
    def test_custom_metadata_schema(self):
        """Use a custom MetaData instance to add a schema."""
        # The use-case for this functionality is to allow using
        # Foreign Data Wrappers, each with a full set of Django
        # tables, to copy between databases using SQLAlchemy
        # and the automatically generation of aldjemy.
        metadata = MetaData(schema="arbitrary")
        sa_models = construct_models(metadata)
        self.assertEqual(sa_models[Log].__table__.schema, "arbitrary")

    def test_custom_metadata_schema_aliased(self):
        """Make sure the aliased command works with the schema."""
        # This was an issue that cropped up after things seemed
        # to be generating properly, so we want to test it and
        # make sure that it stays working.
        metadata = MetaData(schema="pseudorandom")
        sa_models = construct_models(metadata)
        aliased(sa_models[Log])

    def test_many_to_many_through_self(self):
        """Make sure recursive through tables work."""
        through_field = Person._meta.get_field("parents")
        through = through_field.remote_field.through

        metadata = MetaData(schema="unique")
        sa_models = construct_models(metadata)
        self.assertEqual(sa_models[through].__table__.schema, "unique")

    def test_many_to_many_through_self_aliased(self):
        """Make sure aliased recursive through tables work."""
        through_field = Person._meta.get_field("parents")
        through = through_field.remote_field.through

        metadata = MetaData(schema="unique")
        sa_models = construct_models(metadata)
        aliased(sa_models[through])


class ForeignKeyTests(TestCase):
    def test_foreign_key_through_pk(self):
        """Make sure that foreign keys to primary keys work."""
        metadata = MetaData(schema="unique")
        sa_models = construct_models(metadata)
        sa_model = sa_models[RelatedToItemViaPrimaryKey]
        table = sa_model.__table__
        self.assertEqual(len(table.foreign_keys), 1)
        foreign_key, *_ = table.foreign_keys
        foreign_column = foreign_key.column
        item_table = sa_models[Item].__table__
        self.assertIs(foreign_column.table, item_table)
        self.assertEqual(foreign_column.name, "id")
        self.assertEqual(foreign_column.type, item_table.c.id.type)

    def test_foreign_key_through_unique_field(self):
        """Make sure that foreign keys to unique but non primary columns work."""
        metadata = MetaData(schema="unique")
        sa_models = construct_models(metadata)
        sa_model = sa_models[RelatedToItemViaUniqueField]
        table = sa_model.__table__
        self.assertEqual(len(table.foreign_keys), 1)
        foreign_key, *_ = table.foreign_keys
        foreign_column = foreign_key.column
        item_table = sa_models[Item].__table__
        self.assertIs(foreign_column.table, item_table)
        self.assertEqual(foreign_column.name, "legacy_id")
        self.assertEqual(foreign_column.type, item_table.c.legacy_id.type)
