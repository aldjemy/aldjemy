=======
Aldjemy
=======

Small package for integration SQLAlchemy into existents Django project.
Primarily use case of package is building complex queries, that not possible
in Django ORM.

You need to include aldjemy to the end of `INSTALLED_APPS`. On models
importing aldjemy will read all models and contribute `sa` attribute to them.
`sa` attribute is a class, mapped to Table class.

Code example:

    User.sa.query(User.sa.username=='Brubeck')
