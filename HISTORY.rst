2.0 (TBD)
+++++++++

Incompatible changes:

* Dropped support for Python < 3.6.
* Dropped support for Django < 2.2.
* Removed ``aldjemy.to_list``.
* Removed ``aldjemy.core.Cache.models``.
  Use ``aldjemy.core.Cache.sa_models`` instead.

Deprecations:

* Deprecated ``aldjemy.core.Cache`` without a warning or replacement.
