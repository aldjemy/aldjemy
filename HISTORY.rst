2.0 (TBD)
+++++++++

Incompatible changes:

* Dropped support for Python < 3.6.
* Dropped support for Django < 2.2.
* Removed ``aldjemy.to_list``.
* Removed ``aldjemy.core.get_meta``.
* Removed ``aldjemy.core.Cache.models``.
* Removed ``aldjemy.core.Cache.sa_models``.
* Removed ``aldjemy.core.Cache.meta``.
* Removed ``aldjemy.orm.prepare_models``.
* Removed ``aldjemy.table.get_all_django_models``.
* Merged ``aldjemy.types`` and ``aldjemy.postgres`` into ``aldjemy.table``.

Deprecations:

* Deprecated ``aldjemy.core.Cache`` without a warning or replacement.
