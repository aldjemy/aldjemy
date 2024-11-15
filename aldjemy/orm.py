from typing import Callable

from django.apps import apps
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from sqlalchemy import orm
from sqlalchemy.orm import registry

from .table import generate_tables


def _extract_model_attrs(metadata, model, sa_models):
    tables = metadata.tables

    name = model._meta.db_table
    qualname = (metadata.schema + "." + name) if metadata.schema else name
    table = tables[qualname]
    fks = [t for t in model._meta.fields if isinstance(t, (ForeignKey, OneToOneField))]
    attrs = {}
    rel_fields = fks + list(model._meta.many_to_many)

    for f in model._meta.fields:
        if not isinstance(f, (ForeignKey, OneToOneField)):
            if f.model != model or f.column not in table.c:
                continue  # Fields from parent model are not supported
            attrs[f.name] = orm.column_property(table.c[f.column])

    for fk in rel_fields:
        if fk.column not in table.c and not isinstance(fk, ManyToManyField):
            continue

        parent_model = fk.remote_field.model

        parent_model_meta = parent_model._meta

        if parent_model_meta.proxy:
            continue

        p_table_name = parent_model_meta.db_table
        p_table_qualname = (
            metadata.schema + "." + p_table_name if metadata.schema else p_table_name
        )
        p_table = tables[p_table_qualname]
        p_name = parent_model_meta.pk.column

        related_name = fk.remote_field.get_accessor_name()
        disable_backref = related_name and related_name.endswith("+")
        backref = related_name.lower().strip("+") if related_name else None
        if not backref and not disable_backref:
            backref = model._meta.object_name.lower()
            if not isinstance(fk, OneToOneField):
                backref = backref + "_set"
        elif backref and isinstance(fk, OneToOneField):
            backref = orm.backref(backref, uselist=False)

        kwargs = {}
        if isinstance(fk, ManyToManyField):
            model_pk = model._meta.pk.column
            sec_table_name = fk.remote_field.field.m2m_db_table()
            sec_table_qualname = (
                metadata.schema + "." + sec_table_name
                if metadata.schema
                else sec_table_name
            )
            sec_table = tables[sec_table_qualname]
            sec_column = fk.m2m_column_name()
            p_sec_column = fk.m2m_reverse_name()
            overlaps = [
                fk.m2m_field_name(),
                fk.m2m_reverse_field_name(),
                fk.remote_field.field.get_attname(),
                fk.remote_field.through._meta.get_field(
                    fk.remote_field.field.m2m_field_name()
                ).remote_field.get_accessor_name(),
                fk.remote_field.through._meta.get_field(
                    fk.m2m_reverse_field_name()
                ).remote_field.get_accessor_name(),
            ]
            kwargs.update(
                secondary=sec_table,
                primaryjoin=(sec_table.c[sec_column] == table.c[model_pk]),
                secondaryjoin=(sec_table.c[p_sec_column] == p_table.c[p_name]),
                overlaps=",".join(overlaps),
            )
            if fk.model() != model:
                backref = None
        else:
            kwargs.update(
                foreign_keys=[table.c[fk.column]],
                primaryjoin=(table.c[fk.column] == p_table.c[p_name]),
                remote_side=p_table.c[p_name],
            )
            if backref and not disable_backref:
                kwargs.update(backref=backref)
        attrs[fk.name] = orm.relationship(sa_models[parent_model], **kwargs)
    return attrs


def _default_make_sa_model(model):
    """Create a custom class for the SQLAlchemy model."""
    name = model._meta.object_name + ".__aldjemy__"
    return type(name, (), {"__module__": model.__module__})


def construct_models(metadata, *, _make_sa_model: Callable = _default_make_sa_model):
    if not metadata.tables:
        generate_tables(metadata)
    tables = metadata.tables
    models = [
        model
        for model in apps.get_models(include_auto_created=True)
        if not model._meta.proxy
    ]

    sa_models = {}
    for model in models:
        table_name = (
            metadata.schema + "." + model._meta.db_table
            if metadata.schema
            else model._meta.db_table
        )
        table = tables[table_name]
        sa_models[model] = _make_sa_model(model)

    mapper_registry = registry()
    for model in models:
        sa_model = sa_models[model]
        table_name = (
            metadata.schema + "." + model._meta.db_table
            if metadata.schema
            else model._meta.db_table
        )
        table = tables[table_name]
        attrs = _extract_model_attrs(metadata, model, sa_models)
        mapper_registry.map_imperatively(sa_model, local_table=table, properties=attrs)

    return sa_models
