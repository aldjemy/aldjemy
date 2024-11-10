import pytest
from django.contrib.auth import get_user_model
from sqlalchemy import MetaData, select
from sqlalchemy.orm import aliased, Session
from sqlalchemy.sql import func

from aldjemy.engine import create_engine
from aldjemy.orm import construct_models
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

    @pytest.mark.django_db(transaction=True)
    def test_querying(self):
        Book.objects.create(title="book title")
        Book.objects.all()
        with Session(create_engine(), future=True) as session:
            count = session.scalar(select(func.count()).select_from(Book.sa))
            assert count == 1
            result = session.scalars(select(Book.sa)).first()
            assert result.title == "book title"

    @pytest.mark.django_db(transaction=True)
    def test_user_model(self):
        u = User.objects.create()
        Author.objects.create(user=u)

        engine = create_engine('default')
        with Session(engine) as session:
            stmt = select(Author.sa).limit(1)
            a = session.scalar(stmt)
            assert a.user.id == u.id


class TestAliases:

    @pytest.mark.django_db(transaction=True, databases=["default", "logs"])
    def test_logs(self):
        Log.objects.create(record="1")
        Log.objects.create(record="2")
        assert Log.objects.using("logs").count() == 2
        with Session(create_engine("logs"), future=True) as session:
            count = session.scalar(select(func.count()).select_from(Log.sa))
            assert count == 2
            all = session.scalars(select(Log.sa))
            assert [x.record for x in all] == ["1", "2"]


class TestAldjemyMeta:
    @pytest.mark.django_db(transaction=True, databases=["logs"])
    def test_meta(self):
        Log.objects.create(record="foo")
        with Session(create_engine("logs"), future=True) as session:
            foo = session.scalar(select(Log.sa))
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
