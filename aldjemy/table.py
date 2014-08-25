#! /usr/bin/env python

from sqlalchemy import types, Column, Table

from django.conf import settings
try:
    from django.apps import apps as django_apps
except ImportError:
    from django.db.models.loading import AppCache
    django_apps = AppCache()

from aldjemy.types import simple, foreign_key, varchar


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
    'IPAddressField':    lambda field: types.CHAR(length=15),
    'NullBooleanField':  simple(types.Boolean),
    'OneToOneField':     foreign_key,
    'ForeignKey':        foreign_key,
    'PositiveIntegerField': simple(types.Integer),
    'PositiveSmallIntegerField': simple(types.SmallInteger),
    'SlugField':         varchar,
    'SmallIntegerField': simple(types.SmallInteger),
    'TextField':         simple(types.Text),
    'TimeField':         simple(types.Time),
}

DATA_TYPES.update(getattr(settings, 'ALDJEMY_DATA_TYPES', {}))


def get_django_models():
    return django_apps.get_models()


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
    for model in models:
        name = model._meta.db_table
        if name in metadata.tables or model._meta.proxy:
            continue
        columns = []
        for field, parent_model in model._meta.get_fields_with_model():
            if parent_model:
                continue
            typ = DATA_TYPES[field.get_internal_type()](field)
            if not isinstance(typ, (list, tuple)):
                typ = [typ]
            columns.append(Column(field.column,
                    *typ, primary_key=field.primary_key))
        Table(name, metadata, *columns)
