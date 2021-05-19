#! /usr/bin/env python

import sqlalchemy.dialects.postgresql
from django.apps import apps
from django.conf import settings
from sqlalchemy import Column, Table, types

from aldjemy import postgres
from aldjemy.types import foreign_key, simple, varchar

DATA_TYPES = {
    "AutoField": simple(types.Integer),
    "BigAutoField": simple(types.BigInteger),
    "BooleanField": simple(types.Boolean),
    "CharField": varchar,
    "CommaSeparatedIntegerField": varchar,
    "DateField": simple(types.Date),
    "DateTimeField": simple(types.DateTime),
    "DecimalField": lambda x: types.Numeric(
        scale=x.decimal_places, precision=x.max_digits
    ),
    "DurationField": simple(types.Interval),
    "FileField": varchar,
    "FilePathField": varchar,
    "FloatField": simple(types.Float),
    "IntegerField": simple(types.Integer),
    "BigIntegerField": simple(types.BigInteger),
    "IPAddressField": lambda field: types.CHAR(length=15),
    "NullBooleanField": simple(types.Boolean),
    "OneToOneField": foreign_key,
    "ForeignKey": foreign_key,
    "PositiveIntegerField": simple(types.Integer),
    "PositiveSmallIntegerField": simple(types.SmallInteger),
    "SlugField": varchar,
    "SmallIntegerField": simple(types.SmallInteger),
    "TextField": simple(types.Text),
    "TimeField": simple(types.Time),
}


# Update with dialect specific data types
DATA_TYPES["ArrayField"] = lambda field: postgres.array_type(DATA_TYPES, field)
DATA_TYPES["UUIDField"] = simple(sqlalchemy.dialects.postgresql.UUID)


# Update with user specified data types
DATA_TYPES.update(getattr(settings, "ALDJEMY_DATA_TYPES", {}))


def generate_tables(metadata):
    models = apps.get_models(include_auto_created=True)
    for model in models:
        name = model._meta.db_table
        qualname = (metadata.schema + "." + name) if metadata.schema else name
        if qualname in metadata.tables or model._meta.proxy:
            continue
        columns = []
        model_fields = [
            (f, f.model if f.model != model else None)
            for f in model._meta.get_fields()
            if not f.is_relation or f.one_to_one or (f.many_to_one and f.related_model)
        ]
        private_fields = model._meta.private_fields
        for field, parent_model in model_fields:
            if field not in private_fields:
                if parent_model:
                    continue

                try:
                    internal_type = field.get_internal_type()
                except AttributeError:
                    continue

                if internal_type in DATA_TYPES and hasattr(field, "column"):
                    typ = DATA_TYPES[internal_type](field)
                    if not isinstance(typ, (list, tuple)):
                        typ = [typ]
                    columns.append(
                        Column(field.column, *typ, primary_key=field.primary_key)
                    )

        Table(name, metadata, *columns)
