import warnings
from sqlalchemy import orm
import django
from django.db.models.fields.related import (ForeignKey, OneToOneField,
        ManyToManyField)
from django.db import connections, router
from django.db.backends import signals
from django.conf import settings

from .core import get_tables, get_engine, Cache
from .table import get_django_models


def get_session(alias='default'):
    connection = connections[alias]
    if not hasattr(connection, 'sa_session'):
        session = orm.sessionmaker(bind=get_engine(alias))
        connection.sa_session = session()
    return connection.sa_session


def new_session(sender, connection, **kw):
    if connection.alias in settings.DATABASES:
        get_session(alias=connection.alias)

signals.connection_created.connect(new_session)


def get_remote_field(foreign_key):
    if django.VERSION < (1, 8):
        return foreign_key.related
    elif django.VERSION < (1, 9):
        return foreign_key.rel
    return foreign_key.remote_field


def _extract_model_attrs(model, sa_models):
    tables = get_tables()

    name = model._meta.db_table
    table = tables[name]
    fks = [t for t in model._meta.fields
             if isinstance(t, (ForeignKey, OneToOneField))]
    attrs = {}
    rel_fields = fks + list(model._meta.many_to_many)
    for fk in rel_fields:
        if not fk.column in table.c and not isinstance(fk, ManyToManyField):
            continue

        if django.VERSION < (1, 8):
            parent_model = fk.related.parent_model
        else:
            parent_model = get_remote_field(fk).model

        parent_model_meta = parent_model._meta

        p_table = tables[parent_model_meta.db_table]
        p_name = parent_model_meta.pk.column

        if django.VERSION < (1, 9):
            disable_backref = fk.rel.related_name and fk.rel.related_name.endswith('+')
            backref = (fk.rel.related_name.lower().strip('+')
                       if fk.rel.related_name else None)
        else:
            disable_backref = fk.remote_field.related_name and fk.remote_field.related_name.endswith('+')
            backref = (fk.remote_field.related_name.lower().strip('+')
                       if fk.remote_field.related_name else None)
        if not backref and not disable_backref:
            backref = model._meta.object_name.lower()
            if not isinstance(fk, OneToOneField):
                backref = backref + '_set'
        elif backref and isinstance(fk, OneToOneField):
            backref = orm.backref(backref, uselist=False)

        kw = {}
        if isinstance(fk, ManyToManyField):
            model_pk = model._meta.pk.column
            sec_table = tables[get_remote_field(fk).field.m2m_db_table()]
            sec_column = fk.m2m_column_name()
            p_sec_column = fk.m2m_reverse_name()
            kw.update(
                secondary=sec_table,
                primaryjoin=(sec_table.c[sec_column] == table.c[model_pk]),
                secondaryjoin=(sec_table.c[p_sec_column] == p_table.c[p_name])
                )
            if fk.model() != model:
                backref = None
        else:
            kw.update(
                foreign_keys=[table.c[fk.column]],
                primaryjoin=(table.c[fk.column] == p_table.c[p_name]),
                remote_side=p_table.c[p_name],
                )
            if backref:
                kw.update(backref=backref)
        attrs[fk.name] = orm.relationship(
                sa_models[parent_model],
                **kw
                )
    return attrs


def prepare_models():

    tables = get_tables()
    models = get_django_models()

    sa_models_by_django_models = getattr(Cache, 'sa_models', {})

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sa_models_by_table_names = getattr(Cache, 'models', {})

    for model in models:

        table_name = model._meta.db_table
        mixin = getattr(model, 'aldjemy_mixin', None)
        bases = (mixin, BaseSQLAModel) if mixin else (BaseSQLAModel, )
        table = tables[table_name]

        # because querying happens on sqlalchemy side, we can use only one
        # type of queries for alias, so we use 'read' type
        sa_model = type(model._meta.object_name, bases,
                        {'table': table,
                         'alias': router.db_for_read(model)})

        sa_models_by_table_names[table_name] = sa_model
        sa_models_by_django_models[model] = sa_model

    for model in models:
        sa_model = sa_models_by_django_models[model]
        table = tables[model._meta.db_table]
        attrs = _extract_model_attrs(model, sa_models_by_django_models)
        orm.mapper(sa_model, table, attrs)
        model.sa = sa_model

    Cache.sa_models = sa_models_by_django_models
    Cache.models = sa_models_by_table_names


class BaseSQLAModel(object):
    @classmethod
    def query(cls, *a, **kw):
        alias = getattr(cls, 'alias', 'default')
        if a or kw:
            return get_session(alias).query(*a, **kw)
        return get_session(alias).query(cls)
