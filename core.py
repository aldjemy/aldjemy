from django.db import connection
from sqlalchemy import MetaData, create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.pool import _ConnectionRecord as _ConnectionRecordBase

from .table import generate_tables


__all__ = ['get_engine', 'get_meta', 'get_tables']


class Cache(object):
    """Module level cache"""
    pass


SQLALCHEMY_ENGINES = {
    'sqlite3': 'sqlite',
    'mysql': 'mysql',
    'postgresql': 'postgresql',
    'postgresql_psycopg2': 'postgresql+psycopg2',
    'oracle': 'oracle',
}


def get_connection_string():
    sett = connection.settings_dict
    engine = SQLALCHEMY_ENGINES[sett['ENGINE'].rsplit('.')[-1]]
    options = '?charset=utf8' if engine == 'mysql' else ''
    return engine + '://' + options


def get_engine():
    if not getattr(Cache, 'engine', None):
        # we have to use autocommit=True, because SQLAlchemy
        # is not aware of Django transactions
        Cache.engine = create_engine(get_connection_string(),
                                   pool=DjangoPool(creator=None),
                                   execution_options=dict(autocommit=True))
    return Cache.engine


def get_meta():
    if not getattr(Cache, 'meta', None):
        Cache.meta = MetaData()
    return Cache.meta


def get_tables():
    if not getattr(Cache, 'tables_loaded', False):
        generate_tables(get_meta())
        Cache.tables_loaded = True
    return get_meta().tables


class DjangoPool(NullPool):
    def status(self):
        return "DjangoPool"

    def _create_connection(self):
        return _ConnectionRecord(self)

    def recreate(self):
        self.logger.info("Pool recreating")

        return DjangoPool(self._creator,
            recycle=self._recycle,
            echo=self.echo,
            logging_name=self._orig_logging_name,
            use_threadlocal=self._use_threadlocal)


class _ConnectionRecord(_ConnectionRecordBase):
    def __init__(self, pool):
        self.__pool = pool
        self.info = {}

        pool.dispatch.first_connect.exec_once(self.connection, self)
        pool.dispatch.connect(self.connection, self)

    @property
    def connection(self):
        if connection.connection is None:
            connection._cursor()
        return connection.connection

    def close(self):
        pass

    def invalidate(self, e=None):
        pass

    def get_connection(self):
        return self.connection
