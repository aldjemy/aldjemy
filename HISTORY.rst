4.0 (TBD)
+++++++++

Breaking Changes:

* MAJOR: Aldjemy's connection sharing has been removed.
  To make queries with SQLAlchemy, you will need to create a
  separate connection to the database with an SQLAlchemy engine.
  Many related functions and classes have been removed.
  * Dropped the ``Model.sa.query()`` method.
  * Removed the internal ``aldjemy.apps.new_session`` function.
  * Removed the ``aldjemy.session.get_session`` function.
  * Removed the ``aldjemy.session`` module.
  * Removed the ``aldjemy.core.get_engine_string`` function.
  * Removed ``aldjemy.core.Cache``.
  * Removed ``aldjemy.core.get_connection_string`` in favor of
    ``aldjemy.core.get_connection_url``.
  * Removed the ``ALDJEMY_SQLALCHEMY_USE_FUTURE`` setting.
  * Removed the ``aldjemy.sqlite`` and ``aldjemy.wrapper`` modules.

Features:

* ``aldjemy.core.get_connection_url`` creates a URL from a Django
  database suitable for passing SQLAlchemy's ``create_engine``
  function, including credentials and the database name.

3.3 (TBD)
+++++++++

Maintenance:

* Reorganize tests

3.2 (2024-11-15)
++++++++++++++++

Fixes:

* Match the 4.1 version minimum on Django in the pyproject.toml
  to match the extended support matrix in Tox and GitHub actions.

3.1 (2024-11-15)
++++++++++++++++

Features:

* Re-add compatibility with Django 4.1, to be removed in version 4.
* Re-add compatibility with Python 3.8, to be removed in version 4.

Fixes:

* Remove _use_threadlocal in DjangoPool, which has been removed from SQLAlchemy
  pool objects since 1.4.


3.0 (2024-11-04)
++++++++++++++++

Notice:

This is the final major version to permit ``Model.sa.query()``.
It is not compatible with SQLAlchemy 2.0.

Instead, build queries with ``Model.sa`` as SQLAlchemy ORM objects,
then execute the query manually using the django connection:

.. code-block:: python

    from django.db import connection
    compiled = stmt.compile(dialect=postgresql.dialect())
    with connection.cursor() as cursor:
        cursor.execute(compiled.string, compiled.params)


Features:

* Add ability to set ``future`` on SQLAlchemy session and engine
  with the ``ALDJEMY_SQLALCHEMY_USE_FUTURE`` setting.

Incompatible changes:

* Dropped support for Python < 3.9.
* Dropped support for Django < 4.2.
* Removed the ``alias`` property from the generated models.
  It was intended for internal use only.
* Removed the ``table`` property from the generated models.
  It is redundant with the ``__table__`` property.
* Moved the ``get_session`` function from ``aldjemy.orm``
  to ``aldjemy.session``.
* Removed the ``query`` method from models generated
  directly using ``construct_models``.
* Changed the ``__name__`` and ``repr()`` of models generated
  directly using ``construct_models``.
* Moved the ``BaseSQLAModel`` class from ``aldjemy.orm``
  to ``aldjemy.apps``, because it is an implementation detail
  of the default app integration.

Maintenance:

* Add support for Django 4.2-5.1
* Add support for Python 3.11-3.13
* Explicit non-support for SQLAlchemy 2.0

2.6 (2021-10-27)
++++++++++++++++

Fixes:

* ManyToManyField with omitted related_name (#221)

2.5 (2021-10-20)
++++++++++++++++

Fixes:

* Address deprecation warnings for SQLAlchemy 1.4 for duplicate model names (#205)

2.4 (2021-10-07)
++++++++++++++++

Fixes:

* Address some deprecation warnings coming from sqlalchemy 1.4 (#212)

Maintenance:

* adopt isort (#210)

2.3 (2021-09-27)
++++++++++++++++

Fixes:

* Address some deprecation warnings coming from sqlalchemy 1.4 (#197) (#199)

Tests:

* Switch to pytest test runner (#201)

2.2 (2021-08-18)
++++++++++++++++++

Fixes:

* Prevent transactions rollback (#175).
  The goal is to fully delegate transaction management to Django.

2.1 (2021-05-21)
++++++++++++++++

Features:

* Django's ``DateRangeField`` is now handled by default
  as a postgres ``DATERANGE`` type.

Fixes:

* Allow types to be imported from ``aldjemy.tables`` in Django settings
  without raising ``ImproperlyConfigured`` for the settings. (#167)

2.0 (2021-05-20)
++++++++++++++++

Incompatible changes:

* Dropped support for Python < 3.6.
* Dropped support for Django < 2.2.
* Dropped support for SQLALchemy < 1.4.
* Removed ``aldjemy.to_list``.
* Removed ``aldjemy.core.get_meta``.
* Removed ``aldjemy.core.Cache.models``.
* Removed ``aldjemy.core.Cache.sa_models``.
* Removed ``aldjemy.core.Cache.meta``.
* Removed ``aldjemy.orm.prepare_models``.
* Removed ``aldjemy.table.get_all_django_models``.
* Merged ``aldjemy.types`` and ``aldjemy.postgres`` into ``aldjemy.table``.

Features:

* Django's `JSONField` is now handled by default as a postgres `JSONB` type.

Deprecations:

* Deprecated ``aldjemy.core.Cache`` without a warning or replacement.
  To get the ``MetaData`` instance that Aldjemy used
  from a model like ``auth.User``,
  call ``auth.User.sa.model.metadata``.
  If you're wanting to get the Aldjemy model for a through table,
  like the through table for ``auth.User.groups``,
  get the Django model for that through table,
  and then access the ``sa`` attribute as normal by calling
  ``auth.User._meta.get_field('groups').remote_field.through.sa``.

Fixes:

* Silence some warnings from SQLAlchemy 1.4.
  Many to many fields create duplicated active relationships,
  which SQLAlchemy discourages.
  However, this retains backward compatibility
  and seems like a reasonable compromise for translating Django models.
