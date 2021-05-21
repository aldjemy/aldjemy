2.1 (2021-05-21)
++++++++++++++++

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

Fixes:

* Silence some warnings from SQLAlchemy 1.4.
  Many to many fields create duplicated active relationships,
  which SQLAlchemy discourages.
  However, this retains backward compatibility
  and seems like a reasonable compromise for translating Django models.
