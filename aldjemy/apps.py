from django.apps import AppConfig
from django.conf import settings
from django.db import router
from django.db.backends import signals
from sqlalchemy import MetaData

from .orm import construct_models
from .session import get_session


def new_session(sender, connection, **kwargs):
    """Create a new session for the given connection."""
    if connection.alias in settings.DATABASES:
        get_session(alias=connection.alias, recreate=True)


class BaseSQLAModel:
    @classmethod
    def query(cls, *args, **kwargs):
        alias = getattr(cls, "__alias__", "default")
        if args or kwargs:
            return get_session(alias).query(*args, **kwargs)
        return get_session(alias).query(cls)


def _make_sa_model(model):
    """Create a custom class for the SQLAlchemy model."""
    mixin = getattr(model, "aldjemy_mixin", None)
    bases = (mixin, BaseSQLAModel) if mixin else (BaseSQLAModel,)

    # because querying happens on sqlalchemy side, we can use only one
    # type of queries for alias, so we use 'read' type
    return type(
        model._meta.object_name + ".sa",
        bases,
        {
            "__alias__": router.db_for_read(model),
            "__module__": model.__module__,
        },
    )


class AldjemyConfig(AppConfig):
    name = "aldjemy"
    verbose_name = "Aldjemy"

    def ready(self):
        # Patch models with SQLAlchemy models
        models = construct_models(MetaData(), _make_sa_model=_make_sa_model)
        for model, sa_model in models.items():
            model.sa = sa_model

        signals.connection_created.connect(new_session)
