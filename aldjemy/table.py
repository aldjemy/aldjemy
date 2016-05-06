#! /usr/bin/env python

from sqlalchemy import types, Column, Table

import django
from django.conf import settings
try:
    from django.apps import apps as django_apps
except ImportError:
    from django.db.models.loading import AppCache
    django_apps = AppCache()

from aldjemy.types import simple, foreign_key, varchar


DATA_TYPES = {
    'AutoField':         simple(types.Integer),
    'BigAutoField':      simple(types.BigInteger),
    'BooleanField':      simple(types.Boolean),
    'CharField':         varchar,
    'CommaSeparatedIntegerField': varchar,
    'DateField':         simple(types.Date),
    'DateTimeField':     simple(types.DateTime),
    'DecimalField':      lambda x: types.Numeric(scale=x.decimal_places,
                                                 precision=x.max_digits),
    'DurationField':     simple(types.Interval),
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
        if django.VERSION < (1, 9):
            model_fields = model._meta.get_fields_with_model()
        else:
            model_fields = [
                (f, f.model if f.model != model else None)
                for f in model._meta.get_fields()
                if not f.is_relation
                    or f.one_to_one
                    or (f.many_to_one and f.related_model)
            ]
        for field, parent_model in model_fields:
            if parent_model:
                continue

            try:
                internal_type = field.get_internal_type()
            except AttributeError:
                continue

            if internal_type in DATA_TYPES and hasattr(field, 'column'):
                typ = DATA_TYPES[internal_type](field)
                if not isinstance(typ, (list, tuple)):
                    typ = [typ]
                columns.append(Column(field.column,
                        *typ, primary_key=field.primary_key))

        Table(name, metadata, *columns)
