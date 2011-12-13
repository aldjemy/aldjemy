=======
Aldjemy
=======

Whats new?
----------

2011-12-14 Added M2M fields generation. Now we dont generate models for m2m tables.
2011-12-14 Sqlite datetime double conversion fix

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

Code example:

    User.sa.query().filter(User.sa.username=='Brubeck')

Not so shiny example demonstrate that we have M2M issues now:

    User.sa.query().join(User.sa.user_groups).join(User.sa.user_groups.property.mapper.class_.group).filter(Group.sa.name=="GROUP_NAME")

And we can do more better:

    from aldjemy import core
    U2G = core.Cache.models['auth_user_groups']
    User.sa.query().join(U2G.user).join(U2G.group).filter(Group.sa.name=="GROUP_NAME").all()

Explicit joins is part of SQLAlchemy philosophy, so aldjemy cant get you Django expirience.
But aldjemy is not positioned as Django ORM drop-in replacement. Its helper for special situations.

Mixins
------

Often django models have helper function and properties that helps to
represent models data (`__unicode__`), or represent some model based logic.

For integrate it with aldjemy models you can put this methods to separate mixin:

    class TaskMixin(object):
        def __unicode__(self):
            return self.code

    class Task(TaskMixin, models.Model):
        aldjemy_mixin = TaskMixin
        code = models.CharField(_('code'), max_length=32, unique=True)

Viola! You can user `unicode` on aldjemy classes, because this mixin will be
mixed into generated aldjemy model.
