from sqlalchemy import orm
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db import connection
from django.core import signals

from .core import get_tables, get_engine, Cache
from .table import get_django_models


def get_session():
    if not hasattr(connection, 'sa_session'):
        session = orm.create_session()
        session.bind = get_engine()
        connection.sa_session = session
    return connection.sa_session


def new_session(**kw):
    if hasattr(connection, 'sa_session'):
        delattr(connection, 'sa_session')
    get_session()
signals.request_started.connect(new_session)


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
            p_name = parent_model.pk.column

            backref = (fk.rel.related_name.lower().strip('+')
                       if fk.rel.related_name else None)
            if not backref:
                backref = model._meta.object_name.lower()
                if not isinstance(fk, OneToOneField):
                    backref = backref  + '_set'

            attrs[fk.name] = orm.relationship(
                    sa_models[parent_model.db_table],
                    foreign_keys=[table.c[fk.column]],
                    primaryjoin=(table.c[fk.column] == p_table.c[p_name]),
                    backref=backref,
                    remote_side=p_table.c[p_name],
                    )
        name = model._meta.db_table
        orm.mapper(sa_models[name], table, attrs)
        model.sa = sa_models[name]

    Cache.models = sa_models


class BaseSQLAModel(object):
    @classmethod
    def query(cls, *a, **kw):
        if a or kw:
            return get_session().query(*a, **kw)
        return get_session().query(cls)
