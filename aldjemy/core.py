from __future__ import annotations
import functools
import time
from collections import deque

from django.conf import settings
from django.db import connections
from sqlalchemy import create_engine, event, util
from sqlalchemy.engine import base
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.pool import _AdhocProxiedConnection
from sqlalchemy.pool import ConnectionPoolEntry
from sqlalchemy.pool import NullPool
from sqlalchemy.pool import _ConnectionRecord

from sqlalchemy.engine.base import Engine

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


def get_engine_string(alias):
    sett = connections[alias].settings_dict
    return sett["ENGINE"].rsplit(".")[-1]


def get_connection_string(alias="default"):
    engine = SQLALCHEMY_ENGINES[get_engine_string(alias)]
    options = "?charset=utf8" if engine == "mysql" else ""
    return engine + "://" + options


def get_engine(alias="default", **kwargs):
    if alias not in Cache.engines:
        engine_string = get_engine_string(alias)
        if engine_string == "sqlite3":
            kwargs["native_datetime"] = True

        pool = DjangoPool(alias=alias, creator=None)
        if SQLALCHEMY_USE_FUTURE is not None:
            kwargs["future"] = SQLALCHEMY_USE_FUTURE
        Cache.engines[alias] = create_engine(
            get_connection_string(alias), pool=pool, **kwargs
        )
    return Cache.engines[alias]


class DjangoPool(NullPool):
    def __init__(self, alias, *args, **kwargs):
        super(DjangoPool, self).__init__(*args, **kwargs)
        self.alias = alias
        self._aldjemy_handlers_init = False

    def status(self):
        return "DjangoPool"

    def _create_connection(self):
        return _DjangoPoolConnectionRecord(self, self.alias)

    def recreate(self):
        self.logger.info("Pool recreating")

        return DjangoPool(
            self.alias,
            self._creator,
            recycle=self._recycle,
            echo=self.echo,
            logging_name=self._orig_logging_name,
            use_threadlocal=self._use_threadlocal,
        )


def first_connect(
    engine: Engine,
    dbapi_connection: DBAPIConnection,
    connection_record: ConnectionPoolEntry,
) -> None:
    """A custom version of first_connect from sqlalchemy.

    Overridden to avoid rolling back the transaction.

    https://github.com/sqlalchemy/sqlalchemy/blob/e82a5f19e1606500ad4bf6a456c2558d74df24bf/lib/sqlalchemy/engine/create.py#L726
    """
    c = base.Connection(
        engine,
        connection=_AdhocProxiedConnection(dbapi_connection, connection_record),
        _has_events=False,
        # reconnecting will be a reentrant condition, so if the
        # connection goes away, Connection is then closed
        _allow_revalidate=False,
        # dont trigger the autobegin sequence
        # within the up front dialect checks
        _allow_autobegin=False,
    )
    c._execution_options = util.EMPTY_DICT

    # NOTE: The original is run in a try/finally block and uses the
    #       dialect that gets passed into the engine constructor.
    engine.dialect.initialize(c)


class _DjangoPoolConnectionRecord(_ConnectionRecord):
    """A custom version of _ConnectionRecord from sqlalchemy.

    Django handles creating connections and transactions, so we need to
    override things deeply in order to avoid SQLAlchemy from doing it
    as it normally does.

    https://github.com/sqlalchemy/sqlalchemy/blob/e82a5f19e1606500ad4bf6a456c2558d74df24bf/lib/sqlalchemy/pool/base.py#L635
    """

    def __init__(self, pool: DjangoPool, alias: str):
        self.alias = alias
        # self.info = {}  # Just in case, I don't know why this is here.

        self.fairy_ref = None
        self.starttime = time.time()
        self.fresh = True
        self.finalize_callback = deque()

        self.__wrap = False
        self.__aldjemy_handlers_init(pool)
        # init of the dialect now takes place within the connect
        # event, so ensure a mutex is used on the first run
        pool.dispatch.connect.for_modify(pool.dispatch)._exec_w_sync_on_first_run(
            self.dbapi_connection, self
        )
        self.__wrap = True

    def __aldjemy_handlers_init(self, pool: DjangoPool) -> None:
        """Replace SQLAlchemy's handler with ours."""
        if not pool._aldjemy_handlers_init:
            # we assume it's the last one
            previous_handler_wrapper = pool.dispatch.connect.listeners.pop()
            assert (
                previous_handler_wrapper.__name__ == "go"
            )  # wrapped by _once_unless_exception=True
            handler = previous_handler_wrapper.__closure__[0].cell_contents
            assert handler.__name__ == "first_connect", (handler, handler.__name__)

            engine = get_engine(self.alias)
            event.listen(
                pool,
                "connect",
                functools.partial(first_connect, engine),
                _once_unless_exception=True,
            )
            pool._aldjemy_handlers_init = True

    @property
    def dbapi_connection(self):
        connection = connections[self.alias]
        if connection.connection is None:
            connection._cursor()
        if self.__wrap:
            if connection.vendor == "sqlite":
                return SqliteWrapper(connection.connection)
            return Wrapper(connection.connection)
        return connection.connection

    def close(self):
        pass

    def invalidate(self, e=None, soft=False):
        pass

    def get_connection(self):
        return self.dbapi_connection

    def checkin(self):
        pass

    def checkout(cls, pool):
        pass
