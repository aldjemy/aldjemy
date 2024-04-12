from django.apps import apps
from django.conf import settings
from sqlalchemy import Column, ForeignKey, Table, types
from sqlalchemy.dialects.postgresql import ARRAY, DATERANGE, JSONB, UUID


def simple(typ):
    return lambda field: typ()


def varchar(field):
    return types.String(length=field.max_length)


def foreign_key(field):
    parent_model = field.related_model
    target = parent_model._meta
    target_table = target.db_table

    target_field, *composite = field.to_fields
    if composite:
        raise NotImplementedError("Composite Foreign keys are not supported")

    if target_field is None:
        target_field = target.pk.column

    target_internal_type = target.get_field(target_field).get_internal_type()
    target_type = DATA_TYPES[target_internal_type](field)

    return target_type, ForeignKey("%s.%s" % (target_table, target_field))


def array_type(field):
    """Convert ArrayField to SQLAlchemy."""
    internal_type = field.base_field.get_internal_type()
    if internal_type not in DATA_TYPES:
        raise NotImplementedError("Unsupported internal array type.")
    if internal_type == "ArrayField":
        raise NotImplementedError("Multi-dimensional array are not supported.")
    sub_type = DATA_TYPES[internal_type](field.base_field)
    return ARRAY(sub_type)


DATA_TYPES = {
    "AutoField": simple(types.Integer),
    "BigAutoField": simple(types.BigInteger),
    "BooleanField": simple(types.Boolean),
    "CharField": varchar,
    "CommaSeparatedIntegerField": varchar,
    "DateField": simple(types.Date),
    "DateTimeField": simple(types.DateTime),
    "DecimalField": lambda field: types.Numeric(
        scale=field.decimal_places, precision=field.max_digits
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
    # PostgreSQL-specific types
    "ArrayField": array_type,
    "UUIDField": simple(UUID),
    "JSONField": simple(JSONB),
    "DateRangeField": simple(DATERANGE),
}


def generate_tables(metadata):
    # Update with user specified data types
    COMBINED_DATA_TYPES = dict(DATA_TYPES)
    COMBINED_DATA_TYPES.update(getattr(settings, "ALDJEMY_DATA_TYPES", {}))

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

                if internal_type in COMBINED_DATA_TYPES and hasattr(field, "column"):
                    typ = COMBINED_DATA_TYPES[internal_type](field)
                    if not isinstance(typ, (list, tuple)):
                        typ = [typ]
                    columns.append(
                        Column(field.column, *typ, primary_key=field.primary_key)
                    )

        Table(name, metadata, *columns)
