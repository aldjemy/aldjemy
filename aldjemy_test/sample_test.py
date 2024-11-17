import pytest
from django.contrib.auth import get_user_model
from django.db import connections
from sqlalchemy import MetaData
from sqlalchemy.orm import aliased

from aldjemy.core import Cache, get_connection_string, get_engine
from aldjemy.orm import construct_models
from aldjemy.session import get_session
from aldjemy_test.sample.models import (
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


class TestSample:
    def test_aldjemy_initialization(self):
        assert Chapter.sa is not None
        assert Book.sa is not None
        assert Author.sa is not None
        assert StaffAuthor.sa is not None
        assert StaffAuthorProxy.sa is not None
        assert Review.sa is not None
        assert BookProxy.sa is not None
        assert User.sa is not None

        # Automatic Many to Many fields get the ``sa`` property
        books_field = Author._meta.get_field("books")
        assert books_field.remote_field.through.sa is not None

    def test_engine_override_test(self):
        assert get_connection_string() == "sqlite+pysqlite://"

    @pytest.mark.django_db
    def test_querying(self):
        Book.objects.create(title="book title")
        Book.objects.all()
        assert Book.sa.query().count() == 1

    @pytest.mark.django_db
    def test_user_model(self):
        u = User.objects.create()
        Author.objects.create(user=u)
        a = Author.sa.query().first()
        assert a.user.id == u.id


class TestAliases:
    def test_engines_cache(self):
        assert get_engine("default") == Cache.engines["default"]
        assert get_engine("logs") == Cache.engines["logs"]
        assert get_engine() == Cache.engines["default"]
        assert get_engine("default") != get_engine("logs")

    def test_sessions(self):
        session_default = get_session()
        session_default2 = get_session("default")
        assert session_default == session_default2
        session_logs = get_session("logs")
        assert connections["default"].sa_session == session_default
        assert connections["logs"].sa_session == session_logs
        assert session_default != session_logs

    @pytest.mark.django_db(databases=["default", "logs"])
    def test_logs(self):
        Log.objects.create(record="1")
        Log.objects.create(record="2")
        Log.objects.using("logs").count() == 2
        Log.sa.query().count() == 2
        Log.sa.query().all()[0].record == "1"


class TestAldjemyMeta:
    @pytest.mark.django_db(databases=["logs"])
    def test_meta(self):
        Log.objects.create(record="foo")

        foo = Log.sa.query().one()
        assert str(foo) == "foo"
        assert foo.reversed_record == "oof"
        assert not hasattr(foo, "this_is_not_copied")


class TestCustomMetaData:
    def test_custom_metadata_schema(self):
        """Use a custom MetaData instance to add a schema."""
        # The use-case for this functionality is to allow using
        # Foreign Data Wrappers, each with a full set of Django
        # tables, to copy between databases using SQLAlchemy
        # and the automatically generation of aldjemy.
        metadata = MetaData(schema="arbitrary")
        sa_models = construct_models(metadata)
        assert sa_models[Log].__table__.schema == "arbitrary"

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
        assert sa_models[through].__table__.schema == "unique"

    def test_many_to_many_through_self_aliased(self):
        """Make sure aliased recursive through tables work."""
        through_field = Person._meta.get_field("parents")
        through = through_field.remote_field.through

        metadata = MetaData(schema="unique")
        sa_models = construct_models(metadata)
        aliased(sa_models[through])


class TestForeignKey:
    def test_foreign_key_through_pk(self):
        """Make sure that foreign keys to primary keys work."""
        metadata = MetaData(schema="unique")
        sa_models = construct_models(metadata)
        sa_model = sa_models[RelatedToItemViaPrimaryKey]
        table = sa_model.__table__
        assert len(table.foreign_keys) == 1
        foreign_key, *_ = table.foreign_keys
        foreign_column = foreign_key.column
        item_table = sa_models[Item].__table__
        assert foreign_column.table is item_table
        assert foreign_column.name == "id"
        assert foreign_column.type == item_table.c.id.type

    def test_foreign_key_through_unique_field(self):
        """Make sure that foreign keys to unique but non primary columns work."""
        metadata = MetaData(schema="unique")
        sa_models = construct_models(metadata)
        sa_model = sa_models[RelatedToItemViaUniqueField]
        table = sa_model.__table__
        assert len(table.foreign_keys) == 1
        foreign_key, *_ = table.foreign_keys
        foreign_column = foreign_key.column
        item_table = sa_models[Item].__table__
        assert foreign_column.table is item_table
        assert foreign_column.name == "legacy_id"
        assert foreign_column.type == item_table.c.legacy_id.type
