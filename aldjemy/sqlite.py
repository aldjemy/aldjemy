from .wrapper import Wrapper


class SqliteWrapper(Wrapper):

    def wrapper(self, obj):
        return sqlite_wrapper(obj)


def sqlite_wrapper(func):
    from django.db.backends.sqlite3.base import Database

    def null_converter(s):
        return s

    def wrapper(*a, **kw):
        converter = Database.converters.pop('DATETIME')
        Database.register_converter("datetime", null_converter)
        res = func(*a, **kw)
        Database.register_converter("DATETIME", converter)
        return res

    return wrapper
