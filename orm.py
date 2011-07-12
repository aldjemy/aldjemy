from sqlalchemy import orm
from django.db.models.loading import AppCache
from django.db.models.fields.related import ForeignKey

from core import get_tables, get_engine


def get_session():
    session = orm.create_session()
    session.bind = get_engine()
    return session


def prepare_models():
    tables = get_tables()
    ac=AppCache()
    models = ac.get_models()
    sa_models = {}

    for model in models:
        name = model._meta.db_table
        table = tables[name]
        sa_models[name] = type(model._meta.object_name, (BaseSQLAModel, ),
                    {'table': table})

    for model in models:
        name = model._meta.db_table
        table = tables[name]
        fks = [t for t in model._meta.fields if isinstance(t, ForeignKey)]
        attrs = {}
        for fk in fks:
            if not fk.column in table.c:
                print fk.column, model, table.c.keys()
                continue
            parent_model = fk.related.parent_model._meta
            p_table = tables[parent_model.db_table]
            attrs[fk.name] = orm.relationship(
                    sa_models[parent_model.db_table],
                    foreign_keys=[table.c[fk.column]],
                    primaryjoin=(table.c[fk.column] == p_table.c['id']))
        name = model._meta.db_table
        if not 'id' in  sa_models[name].__dict__:
            orm.mapper(sa_models[name], table, attrs)
            model.sqla = sa_models[name]
        


class class_property(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class BaseSQLAModel(object):
    @class_property
    @classmethod
    def query(cls):
        return get_session().query(cls)


def make_sa_model(model, table, attrs):
    sa_model = type(model._meta.object_name, (BaseSQLAModel, ),
                    {'table': table})
    orm.mapper(sa_model, table, attrs)
    return sa_model
