from .wrapper import Wrapper


class SqliteWrapper(Wrapper):
    def wrapper(self, obj):
        return sqlite_wrapper(obj)


def sqlite_wrapper(func):
    from django.db.backends.sqlite3.base import Database

    def null_converter(s):
        if isinstance(s, bytes):
            return s.decode("utf-8")
        return s

    def wrapper(*args, **kwargs):
        converter = Database.converters.pop("DATETIME")
        Database.register_converter("datetime", null_converter)
        res = func(*args, **kwargs)
        Database.register_converter("DATETIME", converter)
        return res

    return wrapper
