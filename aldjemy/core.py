import functools
import time
from collections import deque

from django.conf import settings
from django.db import connections
from sqlalchemy import create_engine, event, util
from sqlalchemy.engine import base
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.pool import NullPool
from sqlalchemy.pool import StaticPool
from sqlalchemy.pool import _ConnectionRecord as _ConnectionRecordBase

from .sqlite import SqliteWrapper
from .wrapper import Wrapper

__all__ = ["get_engine"]


class Cache:
    """Module level cache"""

    engines = {}


SQLALCHEMY_ENGINES = {
    "sqlite3": "sqlite",
    "mysql": "mysql",
    "postgresql": "postgresql",
    "postgresql_psycopg2": "postgresql+psycopg2",
    "oracle": "oracle",
}
SQLALCHEMY_ENGINES.update(getattr(settings, "ALDJEMY_ENGINES", {}))
SQLALCHEMY_USE_FUTURE = getattr(settings, "ALDJEMY_SQLALCHEMY_USE_FUTURE", None)


def get_connection_string(alias="default"):
    engine_string = connections[alias].settings_dict["ENGINE"].rsplit(".")[-1]
    engine = SQLALCHEMY_ENGINES[engine_string]
    options = "?charset=utf8" if engine == "mysql" else ""
    return engine + "://" + options


def get_engine(alias="default") -> Engine:
    # if alias not in Cache.engines:
    url = make_url(get_connection_string(alias))
    dialect = url.get_dialect()

    def creator(*a, **kw):
        conn = connections[alias]
        conn.ensure_connection()
        return conn.connection

    pool = StaticPool(creator)
    Cache.engines[alias] = Engine(pool, dialect, url)
    return Cache.engines[alias]
