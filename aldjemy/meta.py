from django.db.models.base import ModelBase


class AldjemyMeta(ModelBase):
    """Add methods and properties to the SQLAlchemy mapping"""

    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = ModelBase.__new__(cls, name, bases, attrs, **kwargs)

        aldjemy_attrs = {}
        for attr_name, attr in attrs.items():
            if callable(attr) or isinstance(attr, property):
                aldjemy_attrs[attr_name] = attr

        new_class.aldjemy_mixin = type(
            "AldjemyMixin_" + name,
            (object,),
            aldjemy_attrs,
        )

        return new_class
