from sqlalchemy import orm
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db import connection

from .core import get_tables, get_engine, Cache
from .table import get_django_models


def get_session():
    if not hasattr(connection.connection, 'sa_session'):
        session = orm.create_session()
        session.bind = get_engine()
        connection.connection.sa_session = session
    return connection.connection.sa_session


def prepare_models():
    tables = get_tables()
    models = get_django_models()
    sa_models = getattr(Cache, 'models', {})

    for model in models:
        name = model._meta.db_table
        table = tables[name]
        sa_models[name] = type(model._meta.object_name, (BaseSQLAModel, ),
                    {'table': table})

    for model in models:
        name = model._meta.db_table
        if 'id' in  sa_models[name].__dict__:
            continue
        table = tables[name]
        fks = [t for t in model._meta.fields
                 if isinstance(t, (ForeignKey, OneToOneField))]
        attrs = {}
        for fk in fks:
            if not fk.column in table.c:
                continue
            parent_model = fk.related.parent_model._meta
            p_table = tables[parent_model.db_table]
            attrs[fk.name] = orm.relationship(
                    sa_models[parent_model.db_table],
                    foreign_keys=[table.c[fk.column]],
                    primaryjoin=(table.c[fk.column] == p_table.c['id']),
                    backref=fk.rel.related_name
                    )
        name = model._meta.db_table
        orm.mapper(sa_models[name], table, attrs)
        model.sa = sa_models[name]
    Cache.models = sa_models


class class_property(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class BaseSQLAModel(object):
    @class_property
    @classmethod
    def query(cls):
        return get_session().query(cls)
