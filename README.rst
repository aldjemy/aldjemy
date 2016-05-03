=======
Aldjemy
=======

|pypi_downloads| |pypi_version| |pypi_license|

-----


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

Code example:

.. code-block:: python

    User.sa.query().filter(User.sa.username=='Brubeck')

M2M sample:

.. code-block:: python

    User.sa.query().join(User.sa.groups).filter(Group.sa.name=="GROUP_NAME")

Explicit joins is part of SQLAlchemy philosophy, so aldjemy can't get you exactly
the same experience as Django.
But aldjemy is not positioned as Django ORM drop-in replacement. It's a helper for special situations.

We have some stuff in the aldjemy cache too:

.. code-block:: python

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

To integrate it with aldjemy models you can put these methods into a separate mixin:

.. code-block:: python

    class TaskMixin(object):
        def __unicode__(self):
            return self.code

    class Task(TaskMixin, models.Model):
        aldjemy_mixin = TaskMixin
        code = models.CharField(_('code'), max_length=32, unique=True)

Voilà! You can use `unicode` on aldjemy classes, because this mixin will be
mixed into generated aldjemy model.

If you want to expose all methods and properties without creating a
separate mixin class, you can use the `aldjemy.meta.AldjemyMeta`
metaclass:

.. code-block:: python

    from aldjemy.meta import AldjemyMeta

    class Task(models.Model):
        code = models.CharField(_('code'), max_length=32, unique=True)

        def __unicode__(self):
            return self.code

        __metaclass__ = AldjemyMeta

The result is same as with the example above, only you didn't need to
create the mixin class at all.

Also note that with Python 3, the syntax is a bit different:

.. code-block:: python

    class Task(models.Model, metaclass=AldjemyMeta):
        code = models.CharField(_('code'), max_length=32, unique=True)

        def __str__(self):
            return self.code


.. |pypi_downloads| image:: https://img.shields.io/pypi/dm/trafaret.svg?style=flat-square
    :target: https://pypi.python.org/pypi/trafaret
    :alt: Downloads

.. |pypi_version| image:: https://img.shields.io/pypi/v/trafaret.svg?style=flat-square
    :target: https://pypi.python.org/pypi/trafaret
    :alt: Downloads

.. |pypi_license| image:: https://img.shields.io/pypi/l/trafaret.svg?style=flat-square
    :target: https://pypi.python.org/pypi/trafaret
    :alt: Downloads

