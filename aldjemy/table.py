#! /usr/bin/env python

from sqlalchemy import types, Column, Table, ForeignKey
from django.db.models.loading import AppCache


def simple(typ):
    return lambda field: typ()


def varchar(field):
    return types.String(length=field.max_length)


def foreign_key(field):
    target = field.related.parent_model._meta
    target_table = target.db_table
    target_pk = target.pk.column
    return types.Integer, ForeignKey('%s.%s' % (target_table, target_pk))


DATA_TYPES = {
    'AutoField':         simple(types.Integer),
    'BooleanField':      simple(types.Boolean),
    'CharField':         varchar,
    'CommaSeparatedIntegerField': varchar,
    'DateField':         simple(types.Date),
    'DateTimeField':     simple(types.DateTime),
    'DecimalField':      lambda x: types.Numeric(scale=x.decimal_places,
                                                 precision=x.max_digits),
    'FileField':         varchar,
    'FilePathField':     varchar,
    'FloatField':        simple(types.Float),
    'IntegerField':      simple(types.Integer),
    'BigIntegerField':   simple(types.BigInteger),
    'IPAddressField':    lambda field: types.CHAR(lenght=15),
    'NullBooleanField':  simple(types.Boolean),
    'OneToOneField':     foreign_key,
    'ForeignKey':        foreign_key,
    'PositiveIntegerField': simple(types.Integer),
    'PositiveSmallIntegerField': simple(types.SmallInteger),
    'SlugField':         varchar,
    'SmallIntegerField': simple(types.SmallInteger),
    'TextField':         simple(types.UnicodeText),
    'TimeField':         simple(types.Time),
}


def get_django_models():
    ac = AppCache()
    return ac.get_models()


def get_all_django_models():
    models = get_django_models()
    # Get M2M models
    new_models = []
    for model in models:
        for field in model._meta.many_to_many:
            new_model = field.rel.through
            if new_model:
                new_models.append(new_model)
    return models + new_models


def generate_tables(metadata):
    models = get_all_django_models()
    for model in  models:
        name = model._meta.db_table
        if name in metadata.tables:
            continue
        columns = []
        for field, parent_model in model._meta.get_fields_with_model():
            if parent_model:
                continue
            typ = DATA_TYPES[field.get_internal_type()](field)
            if not isinstance(typ, (list, tuple)):
                typ=[typ]
            columns.append(Column(field.column,
                    *typ, primary_key=field.primary_key))
        Table(name, metadata, *columns)
