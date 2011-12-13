class SqliteWrapper(object):
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, attr):
        if attr in ['commit', 'rollback']:
            return nullop
        obj = getattr(self.obj, attr)
        if attr not in ['cursor', 'execute']:
            return obj
        if attr == 'cursor':
            return SqliteWrapper(obj)
        return sqlite_wrapper(obj)

    def __call__(self, *a, **kw):
        self.obj = self.obj(*a, **kw)
        return self


def nullop(*a, **kw):
    return


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
