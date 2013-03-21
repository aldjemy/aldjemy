=======
Aldjemy
=======

Whats new?
----------

2011-12-15:

- Add M2M models generations. Storing them on core.Cache.models.

2011-12-14:

- Added M2M fields generation. Now we dont generate models for m2m tables.
- Sqlite datetime double conversion fix

Before:

- mixins support

Base
----

Small package for integration SQLAlchemy into an existent Django project.
The primary use case of this package is building complex queries that are
not possible with the Django ORM.

You need to include aldjemy at the end of `INSTALLED_APPS`. When models are
imported, aldjemy will read all models and contribute `sa` attribute to them.
`sa` attribute is a class, mapped to Table class.

Internally, aldjemy generates tables from Django models. This is an important
distinction from the standard decision of using SQLAlchemy reflection.

Code example::

    User.sa.query().filter(User.sa.username=='Brubeck')

M2M sample::

    User.sa.query().join(User.sa.groups).filter(Group.sa.name=="GROUP_NAME")

Explicit joins is part of SQLAlchemy philosophy, so aldjemy can't get you exactly
the same experience as Django.
But aldjemy is not positioned as Django ORM drop-in replacement. It's a helper for special situations.

We have some stuff in the aldjemy cache too::

    from aldjemy import core
    core.Cache.models # All generated models
    core.get_tables() # All tables, and M2M tables too

You can use this stuff if you need - maybe you want to build queries with tables, or something like this.


Settings
--------

You can add your own field types to map django types to sqlalchemy ones with
``ALDJEMY_DATA_TYPES`` settings parameter.  
Parameter must be a ``dict``, key is result of ``field.get_internal_type()``,
value must be a one arg function. You can get idea from ``aldjemy.types``.
  
Also it is possible to extend/override list of supported SQLALCHEMY engines
using ``ALDJEMY_ENGINES`` settings parameter.  
Parameter should be a ``dict``, key is substring after last dot from 
Django database engine setting (e.g. ``sqlite3`` from ``django.db.backends.sqlite3``),
value is SQLAlchemy driver which will be used for connection (e.g. ``sqlite``, ``sqlite+pysqlite``).
It could be helpful if you want to use ``django-postgrespool``.


Mixins
------

Often django models have helper function and properties that helps to
represent the model's data (`__unicode__`), or represent some model based logic.

To integrate it with aldjemy models you can put these methods into a separate mixin::

    class TaskMixin(object):
        def __unicode__(self):
            return self.code

    class Task(TaskMixin, models.Model):
        aldjemy_mixin = TaskMixin
        code = models.CharField(_('code'), max_length=32, unique=True)

Voilà! You can use `unicode` on aldjemy classes, because this mixin will be
mixed into generated aldjemy model.
