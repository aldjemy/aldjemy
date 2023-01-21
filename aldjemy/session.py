from django.conf import settings
from django.db import connections
from sqlalchemy import orm

from .core import get_engine

SQLALCHEMY_USE_FUTURE = getattr(settings, "ALDJEMY_SQLALCHEMY_USE_FUTURE", None)


def get_session(alias="default", recreate=False, **kwargs):
    connection = connections[alias]
    if not hasattr(connection, "sa_session") or recreate:
        engine = get_engine(alias, **kwargs)
        kwargs = {"bind": engine}
        if SQLALCHEMY_USE_FUTURE is not None:
            kwargs["future"] = SQLALCHEMY_USE_FUTURE  # pragma: no cover
        session = orm.sessionmaker(**kwargs)
        connection.sa_session = session()
    return connection.sa_session
