2.6 (TBD)
+++++++++

Fixes:

* ManyToManyField with through attribute set (#221)

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
