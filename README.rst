=======
Aldjemy
=======

Small package for integration SQLAlchemy into existent Django project.
Primarily use case of package is building complex queries that not possible
in Django ORM.

You need to include aldjemy to the end of `INSTALLED_APPS`. On models
importing aldjemy will read all models and contribute `sa` attribute to them.
`sa` attribute is a class, mapped to Table class.

Internally aldjemy generate tables from Django models. Its important distinction
from standart decision with reflection.

Code example:

    User.sa.query(User.sa.username=='Brubeck')

Not so shiny example demonstrate that we have M2M issues now:

    User.sa.query.join(User.sa.user_groups).join(User.sa.user_groups.property.mapper.class_.group).filter(Group.sa.name=="GROUP_NAME")

And we can do more better:

    from aldjemy import core
    U2G = core.Cache.models['auth_user_groups']
    User.sa.query.join(U2G.user).join(U2G.group).filter(Group.sa.name=="GROUP_NAME").all()

Explicit joins is part of SQLAlchemy philosophy, so aldjemy cant get you Django expirience.
But aldjemy is not positioned as Django ORM drop-in replacement. Its helper for special situations.
