class Wrapper:
    "Wrapper to disable commit in sqla"

    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, attr):
        if attr in ["commit", "rollback"]:
            return lambda *args, **kwargs: None
        obj = getattr(self.obj, attr)
        if attr not in ["cursor", "execute"]:
            return obj
        if attr == "cursor":
            return type(self)(obj)
        return self.wrapper(obj)

    def wrapper(self, obj):
        "Implement if you need to make your customized wrapper"
        return obj

    def __call__(self, *args, **kwargs):
        self.obj = self.obj(*args, **kwargs)
        return self
