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

Small package for integration SQLAlchemy into existent Django project.
Primarily use case of package is building complex queries that not possible
in Django ORM.

You need to include aldjemy to the end of `INSTALLED_APPS`. On models
importing aldjemy will read all models and contribute `sa` attribute to them.
`sa` attribute is a class, mapped to Table class.

Internally aldjemy generate tables from Django models. Its important distinction
from standart decision with reflection.

Code example::

    User.sa.query().filter(User.sa.username=='Brubeck')

M2M sample::

    User.sa.query().join(User.sa.groups).filter(Group.sa.name=="GROUP_NAME")

Explicit joins is part of SQLAlchemy philosophy, so aldjemy cant get you Django expirience.
But aldjemy is not positioned as Django ORM drop-in replacement. Its helper for special situations.

We have some staff in the aldjemy cache too::

    from aldjemy import core
    core.Cache.models # All generated models
    core.get_tables() # All tables, and M2M tables too

You can use this staff if you need - may be you want to build queries with tables, or something like this.


Mixins
------

Often django models have helper function and properties that helps to
represent models data (`__unicode__`), or represent some model based logic.

To integrate it with aldjemy models you can put this methods to separate mixin::

    class TaskMixin(object):
        def __unicode__(self):
            return self.code

    class Task(TaskMixin, models.Model):
        aldjemy_mixin = TaskMixin
        code = models.CharField(_('code'), max_length=32, unique=True)

Viola! You can use `unicode` on aldjemy classes, because this mixin will be
mixed into generated aldjemy model.
