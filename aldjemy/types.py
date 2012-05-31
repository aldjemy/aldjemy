#coding: utf-8

from sqlalchemy import types, ForeignKey


def simple(typ):
    return lambda field: typ()


def varchar(field):
    return types.String(length=field.max_length)


def foreign_key(field):
    target = field.related.parent_model._meta
    target_table = target.db_table
    target_pk = target.pk.column
    return types.Integer, ForeignKey('%s.%s' % (target_table, target_pk))
