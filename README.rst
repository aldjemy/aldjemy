=======
Aldjemy
=======

.. image:: https://raw.githubusercontent.com/aldjemy/aldjemy/main/logo.png
   :alt: Aldjemy Logo

|pypi_version| |pypi_license| |ci-tests| |codecov| |downloads| |black|


Aldjemy integrates SQLAlchemy into an existing Django project,
to help you build complex queries that are difficult for the Django ORM.

While other libraries use SQLAlchemy reflection to generate SQLAlchemy models,
Aldjemy generates the SQLAlchemy models by introspecting the Django models.
This allows you to better control what properties in a table are being accessed.


Installation
------------

Add ``aldjemy`` to your ``INSTALLED_APPS``.
Aldjemy will automatically add an ``sa`` attribute to all models,
which is an SQLAlchemy ``Model``.

Example:

.. code-block:: python

    User.sa.query().filter(User.sa.username=='Brubeck')
    User.sa.query().join(User.sa.groups).filter(Group.sa.name=="GROUP_NAME")

Explicit joins are part of the SQLAlchemy philosophy,
so don't expect Aldjemy to be a Django ORM drop-in replacement.
Instead, you should use Aldjemy to help with special situations.


Settings
--------

You can add your own field types to map django types to sqlalchemy ones with
``ALDJEMY_DATA_TYPES`` settings parameter.
Parameter must be a ``dict``, key is result of ``field.get_internal_type()``,
value must be a one arg function. You can get idea from ``aldjemy.table``.

Also it is possible to extend/override list of supported SQLALCHEMY engines
using ``ALDJEMY_ENGINES`` settings parameter.
Parameter should be a ``dict``, key is substring after last dot from
Django database engine setting (e.g. ``sqlite3`` from ``django.db.backends.sqlite3``),
value is SQLAlchemy driver which will be used for connection (e.g. ``sqlite``, ``sqlite+pysqlite``).
It could be helpful if you want to use ``django-postgrespool``.


Mixins
------

Often django models have helper function and properties that helps to
represent the model's data (`__str__`), or represent some model based logic.

To integrate it with aldjemy models you can put these methods into a separate mixin:

.. code-block:: python

    class TaskMixin:
        def __str__(self):
            return self.code

    class Task(TaskMixin, models.Model):
        aldjemy_mixin = TaskMixin
        code = models.CharField(_('code'), max_length=32, unique=True)

Voilà! You can use ``__str__`` on aldjemy classes, because this mixin will be
mixed into generated aldjemy model.

If you want to expose all methods and properties without creating a
separate mixin class, you can use the `aldjemy.meta.AldjemyMeta`
metaclass:

.. code-block:: python

    class Task(models.Model, metaclass=AldjemyMeta):
        code = models.CharField(_('code'), max_length=32, unique=True)

        def __str__(self):
            return self.code

The result is same as with the example above, only you didn't need to
create the mixin class at all.

Release Process

---------------

 1. Make a Pull Request with updated changelog and bumped version of the project

    .. code-block:: bash

       hatch version (major|minor|patch) # choose which version to bump

 2. Once the pull request is merged, create a github release with the same version, on the web console or with github cli.

    .. code-block:: bash

       gh release create

 3. Enjoy!

.. |pypi_version| image:: https://img.shields.io/pypi/v/aldjemy.svg
    :target: https://pypi.python.org/pypi/aldjemy
    :alt: Downloads

.. |pypi_license| image:: https://img.shields.io/pypi/l/aldjemy.svg
    :target: https://pypi.python.org/pypi/aldjemy
    :alt: License

.. |ci-tests| image:: https://github.com/aldjemy/aldjemy/actions/workflows/build.yml/badge.svg
   :target: https://github.com/aldjemy/aldjemy/actions/workflows/build.yml
   :alt: Continuous Integration results

.. |codecov| image:: https://codecov.io/gh/aldjemy/aldjemy/branch/main/graph/badge.svg?token=h5nWhlDUgl
   :target: https://codecov.io/gh/aldjemy/aldjemy
   :alt: Code Coverage

.. |downloads| image:: https://pepy.tech/badge/aldjemy
   :target: https://pepy.tech/project/aldjemy
   :alt: Downloads

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000
   :target: https://github.com/psf/black
   :alt: Code style: black
