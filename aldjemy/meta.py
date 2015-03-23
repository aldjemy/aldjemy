from django.db.base import ModelBase


class AldjemyMeta(ModelBase):
    '''Add methods and properties to the SQLAlchemy mapping'''

    def __new__(cls, name, bases, attrs, **kwds):
        new_class = ModelBase.__new__(cls, name, bases, attrs, **kwds)

        aldjemy_attrs = {}
        for name, attr in attrs.items():
            if callable(attr) or isinstance(attr, property):
                aldjemy_attrs[name] = attr

        new_class.aldjemy_mixin = type(
            'AldjemyMixin_' + name, (object,),
            aldjemy_attrs,
        )

        return new_class
